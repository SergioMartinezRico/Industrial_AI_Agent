import os
import psycopg2
from dotenv import load_dotenv

# 1. Cargar claves del archivo .env 
load_dotenv()

# Recuperamos las variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

def create_tables():
    print("🔄 Conectando a la base de datos...")
    
    try:
        # 2. Conexión 
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # 3. Definimos las tablas 
        # (Ordenamos de "independientes" a "dependientes")
        
        commands = [
            # --- TABLAS MAESTRAS (Diccionarios) ---
            """
            CREATE TABLE IF NOT EXISTS roles (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS departments (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
            """,
           
            """
            CREATE TABLE IF NOT EXISTS sentiments (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
            """,
           
            """
            CREATE TABLE IF NOT EXISTS urgencies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
            """,
            
            # --- TABLAS DE DATOS ---
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
            # INTERACCIONES (Ahora todo son IDs)
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
            """
        ]

        # 4. Ejecutamos creación
        for command in commands:
            cursor.execute(command)
        
        print(" Tablas creadas correctamente.")

        # 5. Insertar Datos Maestros (Seeding)
        
        # Diccionario de datos a insertar
        seed_data = {
            "roles": ["Admin", "User", "Manager"],
            "departments": ["Diseño (CAD)", "Simulación (CAE)", "Prototipos", "IT / Soporte"],
            "categories": ["Error Software", "Normativa ISO/ANSI", "Modelado 3D", "Planos 2D", "Licencias"],
            "sentiments": ["Positivo", "Neutro", "Negativo", "Enfadado/Frustrado"],
            "urgencies": ["Baja", "Media", "Alta", "Crítica"]
        }

        # Bucle inteligente para rellenar todas las tablas maestras
        for table, values in seed_data.items():
            for val in values:
                # Usamos SQL dinámico seguro para el nombre de la tabla
                query = f"INSERT INTO {table} (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;"
                cursor.execute(query, (val,))

        conn.commit()
        print(" Datos iniciales insertados.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f" Error conectando o creando tablas: {e}")

if __name__ == "__main__":
    create_tables()