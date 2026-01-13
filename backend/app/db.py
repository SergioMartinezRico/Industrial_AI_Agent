import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Variables globales de conexión
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

def get_db_connection():
    """Establece la conexión con PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"❌ Error crítico conectando a BD: {e}")
        return None

def validar_usuario(user_id):
    conn = get_db_connection()
    if not conn: return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if resultado:
            return resultado[0]
        return None
    except Exception as e:
        print(f"❌ Error validando usuario: {e}")
        return None

def obtener_id_maestro(cursor, tabla, valor_texto):
    # Busca el ID de una categoría/urgencia basado en su nombre
    query = f"SELECT id FROM {tabla} WHERE LOWER(name) = LOWER(%s)"
    cursor.execute(query, (valor_texto,))
    res = cursor.fetchone()
    if res:
        return res[0]
    else:
        return 1 # Fallback de seguridad

def registrar_interaccion(user_id, texto_usuario, datos_ia):
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Traducir nombres a IDs
        cat_id = obtener_id_maestro(cursor, "categories", datos_ia["categoria"])
        sent_id = obtener_id_maestro(cursor, "sentiments", datos_ia["sentimiento"])
        urg_id = obtener_id_maestro(cursor, "urgencies", datos_ia["urgencia"])
        
        # 2. Insertar (La fecha 'timestamp' se pone sola por defecto en la BD)
        query = """
            INSERT INTO interactions 
            (user_id, category_id, sentiment_id, urgency_id, input_text, response_text)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_id, cat_id, sent_id, urg_id, texto_usuario, datos_ia["respuesta"]
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error guardando interacción: {e}")
        if conn: conn.close()
        return False

def obtener_historial(user_id=None, categoria=None):
    """
    Recupera el historial. 
    CORREGIDO: Usa 'timestamp' en lugar de 'created_at'.
    """
    conn = get_db_connection()
    if not conn: return []
    
    try:
        cursor = conn.cursor()
        
        # SELECT con LEFT JOIN para tolerancia a fallos
        query = """
            SELECT 
                i.id, 
                i.input_text, 
                i.response_text, 
                COALESCE(c.name, 'Sin Categoría') as categoria, 
                COALESCE(s.name, 'Neutro') as sentimiento, 
                COALESCE(u.name, 'Media') as urgencia, 
                i.timestamp 
            FROM interactions i
            LEFT JOIN categories c ON i.category_id = c.id
            LEFT JOIN sentiments s ON i.sentiment_id = s.id
            LEFT JOIN urgencies u ON i.urgency_id = u.id
            WHERE 1=1
        """
        
        params = []
        
        if user_id:
            query += " AND i.user_id = %s"
            params.append(user_id)
            
        if categoria:
            query += " AND LOWER(c.name) = LOWER(%s)"
            params.append(categoria)
            
        # Ordenar por TIMESTAMP (nombre correcto en tu BD)
        query += " ORDER BY i.timestamp DESC"
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        historial = []
        for r in rows:
            historial.append({
                "id": r[0],
                "pregunta": r[1],
                "respuesta": r[2],
                "categoria": r[3],
                "sentimiento": r[4],
                "urgencia": r[5],
                "fecha": r[6].strftime("%Y-%m-%d %H:%M:%S") if r[6] else None
            })
            
        cursor.close()
        conn.close()
        return historial

    except Exception as e:
        print(f"❌ Error obteniendo historial: {e}")
        if conn: conn.close()
        return []