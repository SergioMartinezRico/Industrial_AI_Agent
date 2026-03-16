import os
import glob
import json
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Carga las variables de entorno
load_dotenv()

# ==========================================
# 1. CONFIGURACIÓN DEL PIPELINE DE INGESTA
# ==========================================
MODEL_NAME = 'all-MiniLM-L6-v2' 

# Ruta base donde están las 6 subcarpetas
BASE_FOLDER = './manuals' # Cambia esto si tu carpeta principal se llama de otra forma, ej: './docs'

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "industrial_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin_pass")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def reset_vector_table():
    """
    PREPARACIÓN DE LA TABLA VECTORIAL.
    Ahora incluye la columna 'dominio' para el filtrado inteligente.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("🔧 Configurando el esquema vectorial en PostgreSQL...")
    cursor.execute("DROP TABLE IF EXISTS manuals_chunks;")
    
    cursor.execute("""
        CREATE TABLE manuals_chunks (
            id SERIAL PRIMARY KEY,
            source_pdf VARCHAR(200),
            dominio VARCHAR(100),  -- NUEVO: Etiqueta de la taxonomía
            chunk_index INTEGER,
            content TEXT,
            embedding vector(384) 
        );
    """)
    # Opcional pero recomendado: Crear un índice clásico en el dominio para búsquedas ultra rápidas
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dominio ON manuals_chunks(dominio);")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✨ Esquema 'manuals_chunks' listo con soporte para dominios.")

def process_pdfs():
    """
    PIPELINE DE INGESTA DIRIGIDO POR TAXONOMÍA.
    """
    print(f"📥 Cargando el motor de Embeddings ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=250,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    # 1. CARGAR LA TAXONOMÍA
    try:
        with open('taxonomia.json', 'r', encoding='utf-8') as f:
            taxonomia = json.load(f)["carpetas_conocimiento"]
            print(f"🗺️ Taxonomía cargada: {len(taxonomia)} dominios encontrados.")
    except Exception as e:
        print(f"❌ Error leyendo taxonomia.json: {e}")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    total_chunks = 0

    # 2. ITERAR POR CARPETAS SEGÚN EL JSON
    for carpeta_nombre, meta in taxonomia.items():
        dominio_actual = meta["dominio"]
        carpeta_path = os.path.join(BASE_FOLDER, carpeta_nombre)
        
        if not os.path.exists(carpeta_path):
            print(f"⚠️ Aviso: La carpeta {carpeta_path} no existe. Saltando...")
            continue

        pdf_files = glob.glob(os.path.join(carpeta_path, "*.pdf"))
        print(f"\n📂 Procesando Dominio: [{dominio_actual}] - {len(pdf_files)} PDFs encontrados.")

        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            print(f" 📖 Leyendo: {filename}...")
            
            try:
                loader = PyPDFLoader(pdf_path)
                pages = loader.load()
                chunks = text_splitter.split_documents(pages)
                
                texts_only = [chunk.page_content for chunk in chunks]
                embeddings = model.encode(texts_only)

                # Insertar en BD con su DOMINIO
                for i, chunk in enumerate(chunks):
                    vector = embeddings[i].tolist()
                    content = chunk.page_content.replace('\x00', '') 
                    
                    cursor.execute(
                        """
                        INSERT INTO manuals_chunks (source_pdf, dominio, chunk_index, content, embedding)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (filename, dominio_actual, i, content, vector)
                    )
                
                conn.commit()
                total_chunks += len(chunks)
                print(f"    ✅ Insertados {len(chunks)} vectores etiquetados como {dominio_actual}.")

            except Exception as e:
                print(f"    ❌ Error procesando {filename}: {e}")
                conn.rollback() # Evita que un error bloquee la transacción actual

    cursor.close()
    conn.close()
    print(f"\n🎉 ¡ETL VECTORIAL COMPLETADO! Se indexaron {total_chunks} fragmentos perfectamente categorizados.")

if __name__ == "__main__":
    reset_vector_table()
    process_pdfs()