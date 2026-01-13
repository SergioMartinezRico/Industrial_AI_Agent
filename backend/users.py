import os
import random
import psycopg2
from dotenv import load_dotenv

# Cargar conexión
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# Lista de empleados (NO ADMINS)
NOMBRES = [
    "Alvaro", "Andrea", "Diego", "Noha", "David", "Irina", "Matilde", 
    "Estibaliz", "Itxaso", "Rebeca", "Mikel", "Ane", "Zigor", "Iker", 
    "Mafalda", "Miguel"
]

def poblar_usuarios():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
        )
        cursor = conn.cursor()
        print("🚀 Iniciando carga de empleados (Regla: Solo Sergio es Admin)...\n")

        # 1. Identificar IDs de los Roles
        cursor.execute("SELECT id FROM roles WHERE name = 'Admin'")
        res_admin = cursor.fetchone()
        if not res_admin:
            print("❌ Error: No existe el rol 'Admin'. Ejecuta db_setup.py primero.")
            return
        id_admin = res_admin[0]

        # Obtener roles que NO son Admin (para el resto de empleados)
        cursor.execute("SELECT id FROM roles WHERE name != 'Admin'")
        ids_no_admin = [r[0] for r in cursor.fetchall()] # Ej: User, Manager

        cursor.execute("SELECT id FROM departments")
        dept_ids = [d[0] for d in cursor.fetchall()]

        # ---------------------------------------------------------
        # PASO 1: GARANTIZAR QUE SERGIO ES ADMIN
        # ---------------------------------------------------------
        print(f"👑 Asegurando privilegios de Admin para Sergio...")
        dept_it = dept_ids[0] # Asignamos un depto cualquiera (ej: el primero)
        
        # Upsert: Si existe actualiza, si no crea
        query_sergio = """
            INSERT INTO users (username, email, role_id, department_id)
            VALUES ('Sergio', 'sergio@empresa.com', %s, %s)
            ON CONFLICT (username) 
            DO UPDATE SET role_id = %s; 
        """
        cursor.execute(query_sergio, (id_admin, dept_it, id_admin))
        print("   -> Sergio configurado como Admin correctamente.")

        # ---------------------------------------------------------
        # PASO 2: CREAR AL RESTO (SIN PERMISOS DE ADMIN)
        # ---------------------------------------------------------
        count = 0
        for nombre in NOMBRES:
            email = f"{nombre.lower()}@empresa.com"
            
            # Asignación aleatoria PERO excluyendo Admin
            rol_elegido = random.choice(ids_no_admin)
            dept_elegido = random.choice(dept_ids)

            query = """
                INSERT INTO users (username, email, role_id, department_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
                RETURNING id;
            """
            cursor.execute(query, (nombre, email, rol_elegido, dept_elegido))
            
            resultado = cursor.fetchone()
            if resultado:
                print(f"✅ Creado: {nombre} (ID: {resultado[0]})")
                count += 1
            else:
                print(f"⚠️  {nombre} ya existía (se respeta su rol actual).")

        conn.commit()
        cursor.close()
        conn.close()
        print(f"\n🎉 Proceso finalizado. Sergio es el jefe. {count} empleados añadidos.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    poblar_usuarios()