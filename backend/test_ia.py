import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# 1. Cargar secretos (Leemos la GROQ_API_KEY del .env)
load_dotenv()

# Verificación de seguridad (Opcional, pero útil para depurar)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ ERROR: No se ha encontrado la GROQ_API_KEY en el archivo .env")
    exit()

def probar_ia():
    print("🧠 Conectando con el cerebro digital (Groq)...")
    
    # 2. Configurar el Modelo
    # Usamos "llama3-8b-8192" porque es rápido, gratis y muy capaz.
    chat = ChatGroq(
        temperature=0,             # 0 = Respuestas precisas/técnicas (sin alucinaciones)
        model_name="llama-3.1-8b-instant"
    )

    # 3. Definir el "Rol" (Prompt Engineering)
    # Aquí es donde le damos la personalidad de experto en CATIA.
    system_prompt = "Eres un consultor experto en CATIA V5 y dibujo técnico. Responde de forma breve y técnica."
    human_prompt = "{pregunta_usuario}"

    # Creamos la plantilla que une las dos partes
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt),
    ])

    # 4. Crear la Cadena (Chain)
    # LangChain usa el símbolo "|" (pipe) para encadenar: Prompt -> Modelo
    chain = prompt | chat

    # 5. Ejecutar la prueba
    consulta = "Tengo un error al hacer un Pad. Me dice que el perfil no está cerrado. ¿Qué hago?"
    print(f"👤 Usuario pregunta: {consulta}")
    print("⏳ Pensando...")

    try:
        respuesta = chain.invoke({"pregunta_usuario": consulta})
        print("\n🤖 IA Responde:")
        print("-" * 50)
        print(respuesta.content)
        print("-" * 50)
        print("✅ ¡Prueba de conexión exitosa!")
        
    except Exception as e:
        print(f"❌ Error al conectar con Groq: {e}")

if __name__ == "__main__":
    probar_ia()