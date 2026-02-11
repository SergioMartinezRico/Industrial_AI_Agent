import os
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq

# Cargar entorno
load_dotenv()

# --- CONFIGURACIÓN ---
# 1. Tu modelo local de Embeddings (el mismo que usaste para ingestar)
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
# 2. Cliente de Groq (El cerebro que habla)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Conexión DB
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "industrial_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin_pass")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )

def search_knowledge_base(query, top_k=3):
    """
    Convierte tu pregunta en números y busca los 3 trozos de PDF más parecidos.
    """
    print(f"🔎 Buscando información sobre: '{query}'...")
    
    # 1. Vectorizar la pregunta
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_vector = model.encode(query).tolist()

    conn = get_db_connection()
    cursor = conn.cursor()

    # 2. Búsqueda por Similitud de Coseno (La magia de pgvector)
    # El operador '<->' calcula la distancia. Ordenamos por menor distancia.
    cursor.execute("""
        SELECT content, source_pdf 
        FROM manuals_chunks 
        ORDER BY embedding <=> %s::vector 
        LIMIT %s
    """, (query_vector, top_k))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def ask_expert(question):
    # --- FASE 1: RECUPERACIÓN (RAG) ---
    retrieved_docs = search_knowledge_base(question)
    
    if not retrieved_docs:
        print("❌ No encontré información relevante en los manuales.")
        return

    # Preparamos el contexto para la IA
    context_text = ""
    print("\n📚 DOCUMENTACIÓN ENCONTRADA:")
    for i, (content, source) in enumerate(retrieved_docs):
        print(f"   [{i+1}] Del manual: {source}")
        print(f"       Running text: {content[:150]}...") # Mostramos solo el principio
        context_text += f"-- FRAGMENTO {i+1} ({source}):\n{content}\n\n"

    # --- FASE 2: GENERACIÓN (LLM) ---
    print("\n🤔 Consultando al Experto (Groq)...")
    
    prompt = f"""
    Eres un Asistente Experto en Ingeniería Industrial.
    Usa la siguiente INFORMACIÓN DE CONTEXTO para responder a la pregunta del usuario.
    Si la respuesta no está en el contexto, di "No tengo esa información en mis manuales".
    
    CONTEXTO TÉCNICO:
    {context_text}
    
    PREGUNTA DEL USUARIO:
    {question}
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Eres un ingeniero experto y preciso."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile", # Un modelo muy potente y rápido
        temperature=0.0, # Temperatura 0 para máxima precisión técnica
    )

    print("\n🤖 RESPUESTA DEL AGENTE:")
    print("="*60)
    print(chat_completion.choices[0].message.content)
    print("="*60)

if __name__ == "__main__":
    # ¡CAMBIA ESTA PREGUNTA POR ALGO QUE VENGA EN TUS PDFS!
    # Ejemplo: "Que es una tolerancia geometrica?" o "Como hago un sketch en Catia?"
    PREGUNTA = "Explícame cómo se definen las tolerancias geométricas según los manuales."
    
    ask_expert(PREGUNTA)