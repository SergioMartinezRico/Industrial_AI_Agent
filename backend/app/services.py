import os
import json
import re
import psycopg2
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage
from sentence_transformers import SentenceTransformer


# --- SILENCIAR LOGS DE TENSORFLOW ---
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

# Cargar entorno
load_dotenv()

# --- CONFIGURACIÓN DE IA Y MODELOS ---
llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile", 
    api_key=os.getenv("GROQ_API_KEY"),
    #model_kwargs={"response_format": {"type": "json_object"}}
)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# --- GESTIÓN DE BASE DE DATOS Y BÚSQUEDA VECTORIAL ---
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "industrial_db"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "admin_pass")
    )

def buscar_contexto_3dx(query, dominio_filtro="TODOS", top_k=8):
    try:
        query_vector = embedding_model.encode(query).tolist()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Filtro SQL quirúrgico basado en la taxonomía
        if dominio_filtro != "TODOS":
            cursor.execute("""
                SELECT content, source_pdf, dominio 
                FROM manuals_chunks 
                WHERE dominio = %s
                ORDER BY embedding <=> %s::vector 
                LIMIT %s
            """, (dominio_filtro, query_vector, top_k))
        else:
            cursor.execute("""
                SELECT content, source_pdf, dominio 
                FROM manuals_chunks 
                ORDER BY embedding <=> %s::vector 
                LIMIT %s
            """, (query_vector, top_k))
            
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        contexto = ""
        for i, (content, source, dom) in enumerate(results):
            contexto += f"\n-- FUENTE: {source} [{dom}] --\n{content}\n"
        return contexto
    except Exception as e:
        print(f"❌ Error en búsqueda vectorial PostgreSQL: {e}")
        return ""

# --- GESTIÓN DE MEMORIA EN MEMORIA RAM (Session Store) ---
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# --- FUNCIONES DE APOYO ---
def extraer_json_seguro(texto):
    """
    Parser Universal: Protege la integridad del JSON para todos los roles.
    """
    import re
    if not texto:
        return {"respuesta": "Error: Respuesta vacía del motor", "categoria": "Error"}

    # 1. Limpieza de bloques Markdown (común en todos los modelos)
    limpio = re.sub(r'^```json\s*|```$', '', texto.strip(), flags=re.MULTILINE)
    
    try:
        # Intento A: Parseo directo (con permisividad de saltos de línea)
        return json.loads(limpio, strict=False)
    except json.JSONDecodeError:
        # Intento B: Extracción por Regex (por si la IA añade texto extra)
        match = re.search(r"(\{.*\})", limpio, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str, strict=False)
            except Exception as e:
                # Intento C: Sanitización agresiva de caracteres de escape
                print(f"⚠️ [PARSER] Sanitizando caracteres para rescate...")
                # Escapamos los saltos de línea físicos que la IA no escapó
                json_str = json_str.replace('\n', '\\n').replace('\r', '')
                try:
                    return json.loads(json_str, strict=False)
                except:
                    raise ValueError(f"Fallo crítico de formato JSON: {str(e)}")
        raise ValueError("No se pudo detectar una estructura JSON válida.")

def clasificar_intencion_plm(texto_usuario, user_id):
    """
    Enrutador Semántico. Determina el Rol del agente y el Dominio de búsqueda en BD.
    """
    print("🧭 [ENRUTADOR] Analizando la intención del usuario y mapeando dominio...")
    
    historial = get_session_history(str(user_id)).messages
    contexto_previo = "\n".join([f"{msg.type}: {msg.content}" for msg in historial[-4:]]) if historial else "Ninguno"

    prompt_clasificador = f"""
    Eres un Arquitecto Principal de Soluciones PLM.
    Clasifica la siguiente consulta en UNA de estas 5 categorías de Rol:
    1. Consultoría y Procesos
    2. Arquitectura PLM y Modelado
    3. Configuración Core y Seguridad
    4. Integraciones y Migración
    5. Operaciones y Soporte
    
    Además, selecciona el DOMINIO de conocimiento más relevante donde debe buscarse la información:
    - "MQL_CORE": Sintaxis pura, comandos MQL.
    - "EKL_RULES": Lógica de negocio, EKL, Knowledge.
    - "INTEGRATION_JPO": Web Services REST, JPOs, Triggers, Java.
    - "SCHEMA_CONFIG": Tipos, atributos, políticas, seguridad.
    - "BUSINESS_PROCESS": Ciclo de vida, Change Management, BOMs.
    - "UI_FRONTEND": Formularios web, comandos de menú, widgets.
    - "TODOS": Solo si la consulta abarca absolutamente todo o es genérica.
    
    Historial reciente:
    {contexto_previo}

    Consulta actual: "{texto_usuario}"

    Responde ÚNICAMENTE con un JSON válido usando esta estructura exacta:
    {{
        "categoria_id": 3,
        "dominio": "MQL_CORE",
        "justificacion": "Breve motivo"
    }}
    """
    
    try:
        respuesta = llm.invoke([SystemMessage(content=prompt_clasificador)])
        resultado = extraer_json_seguro(respuesta.content)
        categoria_detectada = resultado.get("categoria_id", 5)
        dominio_detectado = resultado.get("dominio", "TODOS")
        print(f"🎯 [ENRUTADOR] Rol: {categoria_detectada} | BD Dominio: {dominio_detectado} -> {resultado.get('justificacion', '')}")
        return int(categoria_detectada), dominio_detectado
    except Exception as e:
        print(f"❌ [ENRUTADOR] Error clasificando. Error: {e}")
        return 5, "TODOS"

# --- DICCIONARIO DE PROMPTS EXPERTOS ---
PROMPTS_EXPERTOS = {
    1: """Eres un Consultor Funcional Senior de PLM en 3DExperience.
Tu objetivo es analizar procesos, tomar requisitos y proponer mejoras. NO des código MQL.
Usa este contexto: {contexto_rag}

REGLA DE FORMATO ESTRICTA Y JUSTIFICACIÓN:
El campo "respuesta" debe ser una cadena JSON válida. Escapa siempre las comillas dobles (\\") y utiliza '\\n' literales para los saltos de línea físicos.
Responde ÚNICAMENTE con un JSON válido usando EXACTAMENTE esta estructura:

{{
    "respuesta": "**1. ANÁLISIS AS-IS:**\\n(Análisis aquí)\\n\\n**2. PROPUESTA TO-BE:**\\n(Propuesta aquí)\\n\\n**3. JUSTIFICACIÓN ESTRATÉGICA (EL PORQUÉ):**\\n(Explica en viñetas por qué esta es la mejor forma de hacerlo: ej. adopción de usuario, estándar OOTB, escalabilidad)\\n\\n**4. ENTREGABLES:**\\n(Entregables)\\n\\n**5. RIESGOS DEL NEGOCIO:**\\n(Riesgos)",
    "categoria": "Consultoría y Procesos",
    "sentimiento": "Neutro",
    "urgencia": "Media"
}}""",

    2: """Eres un Arquitecto de Datos y Soluciones PLM en 3DExperience.
Tu objetivo es diseñar el modelo de datos, estructuras BOM y ciclo de vida.
Usa este contexto: {contexto_rag}

REGLA DE DEFENSA OOTB (OUT-OF-THE-BOX FIRST):
Eres el guardián de la arquitectura estándar. Si el usuario pide un desarrollo a medida (Custom, JPOs, Triggers en Java, etc.) para algo que se puede resolver de forma natural mediante configuración:
1. TIENES PROHIBIDO diseñar la solución custom solicitada.
2. Deniega educadamente la petición custom invocando la regla de "OOTB First".
3. Propón la solución estándar equivalente.

REGLA DE FORMATO ESTRICTA Y JUSTIFICACIÓN:
El campo "respuesta" debe ser una cadena JSON válida. Escapa siempre las comillas dobles (\\") y utiliza '\\n' literales para los saltos de línea.
Responde ÚNICAMENTE con un JSON válido usando EXACTAMENTE esta estructura:

{{
    "respuesta": "**1. ARQUITECTURA PROPUESTA:**\\n(Defiende el estándar OOTB aquí si aplica)\\n\\n**2. OBJETOS Y RELACIONES:**\\n(Redacta objetos)\\n\\n**3. JUSTIFICACIÓN TÉCNICA (EL PORQUÉ):**\\n(Explica en viñetas por qué se diseña así: ej. mantenibilidad, reglas de Dassault, futuras migraciones)\\n\\n**4. OOTB vs CUSTOM:**\\n(Análisis)\\n\\n**5. IMPACTO EN RENDIMIENTO:**\\n(Análisis de rendimiento)",
    "categoria": "Arquitectura PLM",
    "sentimiento": "Neutro",
    "urgencia": "Media"
}}""",

    3: """Eres un Desarrollador Core y Administrador 3DExperience.
Tu objetivo es proporcionar scripts basándote EXCLUSIVAMENTE en este contexto: {contexto_rag}

REGLA DE AUDITORÍA Y DOBLE OPCIÓN (MENTORÍA TÉCNICA):
Si la petición del usuario viola las reglas del "MANUAL CORE: BUENAS PRÁCTICAS" (por ejemplo, pide usar 'select *', o pide CREAR nuevos atributos/tipos sin el prefijo 'CUST_'):
1. Advierte claramente en la sección "2. LÓGICA Y JUSTIFICACIÓN".
2. En "3. SINTAXIS MQL", debes proporcionar DOS opciones (Opción 1: Lo pedido NO RECOMENDADO. Opción 2: Autocorregido RECOMENDADO).
ATENCIÓN CRÍTICA: El prefijo 'CUST_' aplica ÚNICAMENTE a elementos de nueva creación. Si el usuario pide consultar o modificar elementos estándar (OOTB) que ya existen (como los estados 'INWORK' u 'Obsolete', o los tipos 'Part' o 'Document'), TIENES PROHIBIDO añadirles el prefijo 'CUST_'.

REGLA DE ENSAMBLAJE ESTRICTA (FEW-SHOT):
Tienes PROHIBIDO inventar sintaxis. En "3. SINTAXIS MQL", usa SIEMPRE esta plantilla base para bucles:
tcl;
eval {{
    mql start transaction;
    set query_result [split [mql temp query bus 'TIPO' * * where 'current == "ESTADO"' select id dump |] \\n]
    foreach row $query_result {{
        if {{$row != ""}} {{
            set obj_id [lindex [split $row |] 3]
            mql modify bus $obj_id attribute 'NOMBRE_ATRIBUTO' 'NUEVO_VALOR';
        }}
    }}
    mql commit transaction;
}}
exit;

REGLA DE FORMATO JSON ESTRICTA Y JUSTIFICACIÓN: 
El campo "respuesta" debe ser una cadena JSON válida. Escapa siempre las comillas dobles (\\") y utiliza '\\n' literales para los saltos de línea. NO generes saltos de línea físicos. Asegúrate de envolver siempre el código MQL o TCL usando tres acentos graves dentro de la sección 3.
Responde ÚNICAMENTE con un JSON válido usando EXACTAMENTE esta estructura:

{{
    "respuesta": "**1. PRERREQUISITOS:**\\n(Redacta aquí los permisos o requisitos)\\n\\n**2. LÓGICA Y JUSTIFICACIÓN (EL PORQUÉ):**\\n(Explica la lógica y enumera en viñetas POR QUÉ se debe programar así: ej. infraestructura como código, trazabilidad de auditoría, evitar bloqueos)\\n\\n**3. SINTAXIS MQL:**\\n(Muestra aquí el código)\\n\\n**4. ROLLBACK:**\\n(Explica el manejo de errores)",
    "categoria": "Desarrollo Core",
    "sentimiento": "Neutro",
    "urgencia": "Media"
}}""",

    4: """Eres un Arquitecto Senior de 3DExperience. Tienes prohibido usar conocimientos generales de Java de internet. 
USA ÚNICAMENTE LAS REGLAS DEL CONTEXTO RECUPERADO {contexto_rag}.

REGLAS DE ORO PARA EL CÓDIGO:
1. JPO PURO: La clase NO hereda de nada (nada de 'implements Trigger').
2. FIRMA EXACTA: El método debe ser `public int sendToSAP(Context context, String[] args)`.
3. PROHIBIDO ORG.JSON: Está terminantemente PROHIBIDO usar `org.json` o `JSONArray`. Debes construir el JSON manualmente usando `StringBuilder` y `.append()`, tal como indica el Manual Maestro.
4. API REAL: Usa `domObj.getRelatedObjects` con los 10 parámetros obligatorios (relación, tipo, objSelects, relSelects, to, from, recurse, etc.) que aparecen en el documento de referencia.

Si fallas en una sola de estas reglas, el código no compilará y el sistema fallará.

REGLA DE FORMATO JSON:
Responde ÚNICAMENTE con el objeto JSON. El código Java en la sección 5 DEBE estar completo y bien estructurado.

{{
    "respuesta": "**1. SISTEMAS INVOLUCRADOS:**\\n...\\n\\n**2. MAPEO DE ATRIBUTOS:**\\n...\\n\\n**3. ESTRATEGIA DE INTEGRACIÓN:**\\n...\\n\\n**4. JUSTIFICACIÓN (EL PORQUÉ):**\\n...\\n\\n**5. ESTRUCTURA DEL CÓDIGO (JPO COMPLETO):**\\n(Implementación real aquí)\\n\\n**6. CONSIDERACIONES:**\\n...",
    "categoria": "Integraciones y Migración",
    "sentimiento": "Neutro",
    "urgencia": "Media"
}}""",

    5: """Eres un Ingeniero de Soporte L3 y Testing para 3DExperience.
Usa este contexto: {contexto_rag}

REGLA DE FORMATO ESTRICTA Y JUSTIFICACIÓN:
El campo "respuesta" debe ser una cadena JSON válida. Escapa siempre las comillas dobles (\\") y utiliza '\\n' literales para los saltos de línea.
Responde ÚNICAMENTE con un JSON válido usando EXACTAMENTE esta estructura:

{{
    "respuesta": "**1. DIAGNÓSTICO / CAUSA RAÍZ:**\\n(Redacta diagnóstico)\\n\\n**2. PASOS DE RESOLUCIÓN:**\\n(Redacta pasos)\\n\\n**3. JUSTIFICACIÓN DE LA SOLUCIÓN (EL PORQUÉ):**\\n(Explica en viñetas por qué esta es la forma segura de resolverlo sin corromper el entorno)\\n\\n**4. PLAN DE PRUEBAS:**\\n(Redacta plan)\\n\\n**5. PREVENCIÓN:**\\n(Redacta prevención)",
    "categoria": "Soporte y Operaciones",
    "sentimiento": "Neutro",
    "urgencia": "Media"
}}"""
}

# --- PIPELINE PRINCIPAL ---
def analizar_duda_con_ia(texto_usuario, user_id="default"):
    print(f"\n🧠 [RAG-3DX] Procesando consulta de {user_id}...")
    
    # 0. Tu Enrutamiento original
    categoria_id, dominio_filtro = clasificar_intencion_plm(texto_usuario, user_id)
    
    # 1. Tu Recuperación original
    contexto_encontrado = buscar_contexto_3dx(texto_usuario, dominio_filtro)
    print(f"🔍 DEBUG RAG: Recuperados {len(contexto_encontrado)} caracteres del dominio [{dominio_filtro}]")
    
    try:
        # 2. Tu Generación Aumentada con Memoria (INTACTA)
        prompt_base = PROMPTS_EXPERTOS.get(categoria_id, PROMPTS_EXPERTOS[5])

        # Refuerzo visual para que la IA no pinte texto basura fuera del JSON
        instruccion_seguridad = "\n\nIMPORTANTE: Responde EXCLUSIVAMENTE con el objeto JSON. No añadas texto introductorio ni bloques Markdown fuera del JSON."

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", prompt_base + instruccion_seguridad),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{consulta}")
        ])
        
        chain = prompt_template | llm
        
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="consulta",
            history_messages_key="history"
        )

        # Tu ejecución original de la cadena
        response_msg = chain_with_history.invoke(
            {
                "consulta": texto_usuario,
                "contexto_rag": contexto_encontrado
            },
            config={"configurable": {"session_id": str(user_id)}}
        )
        print("\n=== RAW LLM OUTPUT ===")
        print(repr(response_msg.content))
        print("======================\n")
        
        # --- BLOQUE DE LIMPIEZA POST-GENERACIÓN ---
        # Esto previene que si la IA escribe ```json { ... } ``` el parser falle.
        contenido = response_msg.content.strip()
        
        # Eliminamos posibles envoltorios de Markdown que Groq añade a veces por su cuenta
        if contenido.startswith("```"):
            # Usamos regex para quedarnos solo con lo que hay entre llaves
            import re
            match = re.search(r"(\{.*\})", contenido, re.DOTALL)
            if match:
                contenido = match.group(1)
        
        # Retornamos usando tu nuevo parser flexible
        return extraer_json_seguro(contenido)

    except Exception as e:
        print(f"❌ Error en Pipeline RAG: {e}")
        return {
            "respuesta": f"Error técnico en el motor: {str(e)}",
            "categoria": "Administración",
            "sentimiento": "Neutro",
            "urgencia": "Alta"
        }