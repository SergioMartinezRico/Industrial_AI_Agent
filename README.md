🚀 3DExperience Expert Advisor - RAG Architecture
Este proyecto implementa un Asistente Inteligente de Ingeniería Senior basado en IA Generativa y arquitectura RAG (Retrieval-Augmented Generation). A diferencia de un chatbot genérico, este sistema está especializado en el ecosistema PLM 3DExperience, resolviendo consultas complejas de consultoría, desarrollo de código (JPO/MQL) e infraestructura.

📋 Descripción del Proyecto
El sistema utiliza un flujo de procesamiento avanzado para transformar manuales técnicos confidenciales en respuestas ejecutables, estructurando la información en metadatos analíticos (categoría, sentimiento y urgencia) para su gestión en una base de datos relacional.

Características Principales:
Enrutador de Dominio: Clasifica la intención del usuario entre 5 roles expertos para recuperar el contexto más preciso.

Manual Maestro (Golden Docs): Prioriza estándares de desarrollo nativos (DomainObject, StringBuilder) para eliminar alucinaciones técnicas.

Universal JSON Parser: Mecanismo de limpieza de pre-vuelo que asegura la integridad de la respuesta incluso con bloques de código extensos.

Memoria de Sesión Dinámica: Mantiene el contexto de conversaciones técnicas complejas mediante LangChain.

🛠️ Stack Tecnológico
AI & Backend
LLM: LLaMA-3.3-70b (vía Groq API) - Inferencia de baja latencia.

Orquestación: LangChain (Chains & Message History).

Vector DB: FAISS / ChromaDB para almacenamiento de embeddings técnicos.

Lenguaje: Python 3.x con Flask.

Datos e Infraestructura
Base de Datos: PostgreSQL 16.x (Modelo normalizado con tablas maestras).

Contenedores: Docker & Docker Compose.

Cloud: Despliegue escalable en AWS (EC2 para App Server y RDS para base de datos).

🏗️ Arquitectura del Sistema
La solución emplea una arquitectura desacoplada orientada a la fiabilidad del dato:

Capa de Ingesta: Procesa PDFs de ingeniería y manuales de JPO, fragmentando el texto y generando embeddings vectoriales.

Capa de Inteligencia (Pipeline RAG):

Router: Mapea la consulta al dominio correspondiente (Core, Schema, JPO, etc.).

Retriever: Recupera los fragmentos más relevantes del "Manual Maestro".

Generator: Produce una respuesta estructurada en JSON validada por el Universal Parser.

Capa de Persistencia: Almacena cada interacción para análisis posterior de performance y sentimiento del usuario.

🚀 Instalación y Despliegue (Local)
Clonar y Configurar:

Bash
git clone <url-del-repositorio>
cd <nombre-carpeta>
Variables de Entorno: Crea un archivo .env con tu GROQ_API_KEY y credenciales de DB.

Iniciar Docker:

Bash
docker-compose up --build
⚠️ Nota sobre Seguridad: Los manuales técnicos de 3DExperience y los índices vectoriales contienen propiedad intelectual y han sido excluidos de este repositorio via .gitignore.

Autor: Sergio Martínez Rico
