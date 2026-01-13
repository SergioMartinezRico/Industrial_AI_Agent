import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

def probar_json():
    print("🧠 Analizando solicitud con estructura de datos...")
    
    # 1. Configuración
    chat = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")
    
    # 2. Listas EXACTAS de nuestra Base de Datos
    categorias = ["Error Software", "Normativa ISO/ANSI", "Modelado 3D", "Planos 2D", "Licencias"]
    sentimientos = ["Positivo", "Neutro", "Negativo", "Enfadado/Frustrado"]
    urgencias = ["Baja", "Media", "Alta", "Crítica"]

    # 3. El Prompt "Ingeniero de Datos"
    # CORRECCIÓN: Usamos {{{{ y }}}} para el ejemplo JSON.
    # Así LangChain sabe que son llaves literales y no variables.
    
    system_prompt = f"""
    Eres un asistente experto en CATIA y un clasificador de datos.
    Tu tarea es:
    1. Responder a la duda del usuario brevemente.
    2. Clasificar la consulta eligiendo UNA opción de cada lista.
    
    LISTAS VÁLIDAS:
    - Categorías: {categorias}
    - Sentimientos: {sentimientos}
    - Urgencias: {urgencias}
    
    FORMATO DE SALIDA (JSON PURO):
    {{{{
        "respuesta": "Tu respuesta técnica aquí...",
        "categoria": "Una de la lista",
        "sentimiento": "Uno de la lista",
        "urgencia": "Uno de la lista"
    }}}}
    NO escribas nada más fuera del JSON.
    """

    human_prompt = "{consulta}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt),
    ])

    # 4. Parser y Cadena
    parser = JsonOutputParser()
    chain = prompt | chat | parser

    # 5. Prueba
    pregunta = "¡Maldita sea! El CATIA se ha cerrado otra vez sin guardar y he perdido todo el trabajo. ¡Es urgente!"
    
    print(f"👤 Usuario: {pregunta}")
    print("⏳ Procesando...")

    try:
        resultado = chain.invoke({"consulta": pregunta})
        
        print("\n📦 RESULTADO JSON RECIBIDO:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        
        # Validación
        print("\n📊 Extracción de datos:")
        print(f"- Respuesta IA: {resultado['respuesta'][:50]}...")
        print(f"- Categoría detectada: {resultado['categoria']}")
        print(f"- Sentimiento detectado: {resultado['sentimiento']}")
        print(f"- Urgencia detectada: {resultado['urgencia']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    probar_json()