import os
import glob
from typing import List
import psycopg2
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import numpy as np

load_dotenv()

# --- CONFIGURACIÓN ---
# Usamos un modelo 'Mini' que es MUY rápido y corre en tu CPU sin problemas.
# Genera vectores de 384 dimensiones.
MODEL_NAME = 'all-MiniLM-L6-v2' 
PDF_FOLDER = './manuals'

# Conexión DB
DB_HOST = os.getenv("DB_HOST", "db")
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
    IMPORTANTE: Recrea la tabla para asegurar que la dimensión del vector
    coincide con el modelo local (384 dimensiones).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("🔧 Ajustando base de datos para modelo local (384 dim)...")
    cursor.execute("DROP TABLE IF EXISTS manuals_chunks;")
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
    print("✨ Tabla 'manuals_chunks' lista y calibrada.")

def process_pdfs():
    # 1. Cargar el modelo de IA (Se descargará la primera vez)
    print(f"📥 Cargando modelo de IA ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)
    
    # 2. Buscar PDFs
    pdf_files = glob.glob(os.path.join(PDF_FOLDER, "*.pdf"))
    if not pdf_files:
        print(f"❌ No encontré PDFs en {PDF_FOLDER}. ¡Mete tus manuales de CATIA ahí!")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    total_chunks = 0

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"📖 Leyendo: {filename}...")
        
        try:
            reader = PdfReader(pdf_path)
            text_chunks = []
            
            # Estrategia simple: 1 trozo = 1 página (para empezar)
            # En producción usaríamos un "RecursiveCharacterTextSplitter" de LangChain
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and len(text) > 50: # Ignorar páginas vacías o con poquísimo texto
                    # Limpieza básica
                    text = text.replace('\n', ' ').strip()
                    text_chunks.append((i, text))
            
            if not text_chunks:
                print(f"⚠️ {filename} parece vacío o no se pudo leer texto.")
                continue

            # 3. Vectorizar (Convertir texto a números)
            print(f"   🧠 Vectorizando {len(text_chunks)} páginas...")
            texts_only = [chunk[1] for chunk in text_chunks]
            embeddings = model.encode(texts_only) # Aquí ocurre la magia matemática

            # 4. Guardar en Base de Datos
            print(f"   💾 Guardando en Postgres...")
            for i, (page_num, text) in enumerate(text_chunks):
                vector = embeddings[i].tolist()
                
                cursor.execute(
                    """
                    INSERT INTO manuals_chunks (source_pdf, chunk_index, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (filename, page_num, text, vector)
                )
            
            conn.commit()
            total_chunks += len(text_chunks)
            print(f"   ✅ {filename} procesado.")

        except Exception as e:
            print(f"   ❌ Error leyendo {filename}: {e}")

    cursor.close()
    conn.close()
    print(f"\n🎉 ¡PROCESO TERMINADO! Se han indexado {total_chunks} fragmentos de información.")
    print("Ahora tu IA ya 'sabe' sobre CATIA.")

if __name__ == "__main__":
    reset_vector_table()
    process_pdfs()