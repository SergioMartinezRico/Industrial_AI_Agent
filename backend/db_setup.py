import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Configuración de conexión (Docker inyecta estas variables automáticamente)
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "industrial_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin_pass")

def create_tables():
    print("🔄 Conectando a la Base de Datos Híbrida...")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # --- 1. ACTIVAR LA INTELIGENCIA VECTORIAL ---
        # Esta es la línea MÁGICA. Habilita las matemáticas para la IA.
        print("🧠 Activando extensión pgvector...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # --- 2. DEFINIR TABLAS ---
        commands = [
            # Tablas Auxiliares (Para que sea profesional)
            "CREATE TABLE IF NOT EXISTS roles (id SERIAL PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL)",
            "CREATE TABLE IF NOT EXISTS departments (id SERIAL PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL)",
            "CREATE TABLE IF NOT EXISTS categories (id SERIAL PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL)",
            "CREATE TABLE IF NOT EXISTS sentiments (id SERIAL PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL)",
            "CREATE TABLE IF NOT EXISTS urgencies (id SERIAL PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL)",
            
            # Tabla de Usuarios
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) NOT NULL,
                role_id INTEGER REFERENCES roles(id),
                department_id INTEGER REFERENCES departments(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Tabla de Interacciones (Chat Logs)
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                category_id INTEGER REFERENCES categories(id),
                input_text TEXT NOT NULL,
                response_text TEXT NOT NULL,
                sentiment_id INTEGER REFERENCES sentiments(id),
                urgency_id INTEGER REFERENCES urgencies(id),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # --- NUEVA TABLA PARA RAG (MANUALES TÉCNICOS) ---
            # Aquí guardamos los manuales troceados y sus vectores
            """
            CREATE TABLE IF NOT EXISTS manuals_chunks (
                id SERIAL PRIMARY KEY,
                source_pdf VARCHAR(200),
                chunk_index INTEGER,
                content TEXT,
                embedding vector(1536)  -- Vector compatible con modelos actuales
            )
            """
        ]

        print("🏗️ Creando tablas...")
        for command in commands:
            cursor.execute(command)
        
        # --- 3. DATOS BÁSICOS (SEEDING) ---
        # Insertamos valores por defecto para que no esté vacía
        seed_data = {
            "roles": ["Admin", "User", "Manager"],
            "departments": ["Mantenimiento", "Ingeniería", "Operaciones"],
            "categories": ["Fallo Mecánico", "Fallo Eléctrico", "Software", "Seguridad"],
            "sentiments": ["Positivo", "Neutro", "Negativo"],
            "urgencies": ["Baja", "Media", "Alta", "Crítica"]
        }

        for table, values in seed_data.items():
            for val in values:
                cursor.execute(f"INSERT INTO {table} (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (val,))

        conn.commit()
        print("✅ ¡Base de Datos inicializada con éxito!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    create_tables()