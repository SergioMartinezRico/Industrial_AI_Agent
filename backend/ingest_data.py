import os
import glob
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# ==========================================
# 1. CONFIGURACIÓN DEL PIPELINE DE INGESTA
# ==========================================

# Modelo de Embeddings: Usamos 'all-MiniLM-L6-v2'. 
# Es un modelo local, ultraligero y muy rápido que genera vectores de 384 dimensiones.
# Ideal para entornos donde no queremos depender (ni pagar) por la API de OpenAI para embeddings.
MODEL_NAME = 'all-MiniLM-L6-v2' 

# Ruta donde el contenedor o el script buscará los manuales PDF de 3DExperience
PDF_FOLDER = './manuals'

# Credenciales de conexión a la base de datos (inyectadas vía Docker/env)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "industrial_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin_pass")

def get_db_connection():
    """
    Establece la conexión con la base de datos PostgreSQL.
    Es vital que la extensión pgvector esté habilitada en esta BD.
    """
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def reset_vector_table():
    """
    PREPARACIÓN DE LA TABLA VECTORIAL.
    Elimina y recrea la tabla 'manuals_chunks'. 
    Esto es una buena práctica en la fase de desarrollo para evitar 
    conflictos si cambiamos el tamaño del chunk o el modelo de embeddings.
    Nota crítica: El tipo de dato 'vector(384)' debe coincidir EXACTAMENTE 
    con la dimensión de salida del modelo SentenceTransformer.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("🔧 Configurando el esquema vectorial en PostgreSQL...")
    cursor.execute("DROP TABLE IF EXISTS manuals_chunks;")
    
    # Creamos la tabla con soporte nativo para vectores matemáticos
    cursor.execute("""
        CREATE TABLE manuals_chunks (
            id SERIAL PRIMARY KEY,
            source_pdf VARCHAR(200),
            chunk_index INTEGER,
            content TEXT,
            embedding vector(384) 
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✨ Esquema 'manuals_chunks' listo y calibrado a 384 dimensiones.")

def process_pdfs():
    """
    PIPELINE PRINCIPAL DE INGESTA (ETL para RAG).
    Lee los PDFs, los divide semánticamente, los convierte a vectores 
    y los almacena en PostgreSQL.
    """
    print(f"📥 Cargando el motor de Embeddings ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)
    
    # Escaneamos el directorio en busca de nuestros manuales
    pdf_files = glob.glob(os.path.join(PDF_FOLDER, "*.pdf"))
    if not pdf_files:
        print(f"❌ No se encontraron archivos PDF en la ruta: {PDF_FOLDER}.")
        return

    # ==========================================
    # 2. ESTRATEGIA DE CHUNKING (DIVISIÓN LÓGICA)
    # ==========================================
    # Para dominios técnicos como 3DExperience (MQL, XML, Java), no podemos cortar
    # a la mitad de un bloque de código. 
    # Usamos RecursiveCharacterTextSplitter para un particionado inteligente:
    # - chunk_size: Máximo de caracteres por bloque (1000 es un buen equilibrio para Llama 3).
    # - chunk_overlap: Solapamiento de 250 caracteres. Si un comando MQL cae en la frontera,
    #   se incluirá al final de un chunk y al principio del siguiente. Evita "amnesia de contexto".
    # - separators: Intenta cortar primero por doble salto de línea (párrafos), 
    #   luego salto simple, etc., protegiendo así la integridad de los bloques de código.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=250,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    conn = get_db_connection()
    cursor = conn.cursor()
    total_chunks = 0

    # Iteramos sobre cada manual encontrado
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"\n📖 Iniciando procesamiento de: {filename}...")
        
        try:
            # 2.1 EXTRACCIÓN
            # LangChain PyPDFLoader respeta mejor la estructura del documento que pypdf nativo
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            
            # 2.2 TRANSFORMACIÓN (Troceado)
            chunks = text_splitter.split_documents(pages)
            print(f"   ✂️ Documento particionado en {len(chunks)} fragmentos (con solapamiento).")
            
            # Extraemos puramente el texto para la vectorización
            texts_only = [chunk.page_content for chunk in chunks]
            
            # 2.3 VECTORIZACIÓN (Embeddings)
            # Pasamos la lista de textos al modelo IA. Devuelve una matriz matemática.
            print(f"   🧠 Generando matrices matemáticas para {len(texts_only)} fragmentos...")
            embeddings = model.encode(texts_only)

            # 2.4 CARGA (Load a BBDD)
            print(f"   💾 Escribiendo vectores en PostgreSQL...")
            for i, chunk in enumerate(chunks):
                vector = embeddings[i].tolist() # Convertimos matriz numpy a lista estándar de Python
                
                # Saneamiento de datos: PostgreSQL rechaza los bytes nulos (\x00) en campos tipo TEXT.
                # Al extraer texto de PDFs complejos, a veces se cuelan estos caracteres fantasma.
                content = chunk.page_content.replace('\x00', '') 
                
                # Insertamos el texto original junto con su representación matemática
                cursor.execute(
                    """
                    INSERT INTO manuals_chunks (source_pdf, chunk_index, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (filename, i, content, vector)
                )
            
            # Hacemos commit por cada archivo completado
            conn.commit()
            total_chunks += len(chunks)
            print(f"   ✅ {filename} indexado exitosamente.")

        except Exception as e:
            # Manejo de errores por archivo para que un PDF corrupto no detenga todo el pipeline
            print(f"   ❌ Error crítico procesando {filename}: {e}")

    # Cierre seguro de conexiones
    cursor.close()
    conn.close()
    print(f"\n🎉 ¡ETL VECTORIAL COMPLETADO! La base de datos ha ingerido {total_chunks} fragmentos de conocimiento técnico.")

if __name__ == "__main__":
    # Ejecutamos el reseteo de tabla y luego la ingesta
    reset_vector_table()
    process_pdfs()