import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Cargar entorno
load_dotenv()

# Configuración IA (Usamos un modelo potente para que no pierda el formato JSON al conversar)
# Recomendado: llama-3.3-70b-versatile o llama-3.1-8b-instant
llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile", 
    api_key=os.getenv("GROQ_API_KEY"),
    model_kwargs={"response_format": {"type": "json_object"}}
)

# Listas Maestras
CATEGORIAS = ["Error Software", "Normativa ISO/ANSI", "Modelado 3D", "Planos 2D", "Licencias"]
SENTIMIENTOS = ["Positivo", "Neutro", "Negativo", "Enfadado/Frustrado"]
URGENCIAS = ["Baja", "Media", "Alta", "Crítica"]

# --- GESTIÓN DE MEMORIA ---
# Diccionario para guardar el historial de cada usuario (en memoria RAM)
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Devuelve el historial de chat asociado a un ID de sesión (ID usuario)"""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# --- PROMPT DEL SISTEMA ---
# Le añadimos la instrucción de que considere el historial
system_prompt = f"""
Eres el Asistente Técnico del CAU de Ingeniería.

TUS REGLAS DE ORO:
1. Utiliza el contexto del historial de conversación para responder mejor.
2. SOLO respondes preguntas sobre CATIA, SolidWorks, AutoCAD, Ingeniería o Soporte TI.
3. Si el usuario pregunta sobre temas no técnicos (cocina, deportes...):
   - Responde AMABLEMENTE rechazando la pregunta.
   - Clasifica como: Categoria="Otros", Sentimiento="Neutro", Urgencia="Baja".

FORMATO OBLIGATORIO (JSON):
Incluso si estás respondiendo a una aclaración sobre una pregunta anterior, 
TU SALIDA DEBE SER SIEMPRE Y ÚNICAMENTE UN JSON VÁLIDO con esta estructura:
{{{{
    "respuesta": "Texto de tu respuesta conversacional aquí...",
    "categoria": "Una de: {CATEGORIAS}",
    "sentimiento": "Uno de: {SENTIMIENTOS}",
    "urgencia": "Uno de: {URGENCIAS}"
}}}}
"""

# Configuración del Prompt con Placeholder para historial
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"), # <--- AQUÍ SE INYECTA LA MEMORIA
    ("human", "{consulta}")
])

# Creamos la cadena BÁSICA (sin historia aún)
# Nota: No metemos el JsonOutputParser dentro de la cadena de historia 
# porque LangChain necesita guardar texto plano en el historial, no diccionarios.
chain = prompt | llm 

# Creamos la cadena CON MEMORIA
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="consulta",
    history_messages_key="history"
)
# --- FUNCIÓN DE LIMPIEZA (LA CIRUGÍA) ---
def extraer_json_seguro(texto):
    """
    Busca el primer '{' y el último '}' para ignorar texto introductorio.
    """
    try:
        # Intentamos parsear directo primero
        return json.loads(texto)
    except json.JSONDecodeError:
        # Si falla, usamos regex para encontrar el objeto JSON entre el ruido
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            raise ValueError("No se encontró JSON válido en la respuesta")
        
def analizar_duda_con_ia(texto_usuario, user_id="default"):
    print(f"🧠 [IA] User {user_id}: '{texto_usuario}'")
    
    try:
        response_msg = chain_with_history.invoke(
            {"consulta": texto_usuario},
            config={"configurable": {"session_id": str(user_id)}}
        )
        
        content_text = response_msg.content
        
        # Usamos el extractor seguro en lugar de un simple json.loads
        resultado_dict = extraer_json_seguro(content_text)
        return resultado_dict

    except Exception as e:
        print(f"❌ Error en Groq/Parsing: {e}")
        # Imprimimos lo que intentó parsear para depurar
        # print(f"   Contenido recibido: {content_text if 'content_text' in locals() else 'Nada'}")
        
        return {
            "respuesta": "Lo siento, la IA ha tenido un problema técnico momentáneo.",
            "categoria": "Error Software",
            "sentimiento": "Neutro",
            "urgencia": "Media"
        }