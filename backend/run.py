import sys
# Esto asegura que Python encuentre la carpeta app
sys.path.append('.')

from app.db import validar_usuario, registrar_interaccion
from app.services import analizar_duda_con_ia

def main():
    print("\n========================================")
    print("🔐  PROTOTIPO CAU - CONSOLA DE PRUEBAS")
    print("========================================")
    
    # --- PASO 1: LOGIN ---
    # Simulamos lo que haría la pantalla de login de la web
    user_id = None
    nombre_usuario = None
    
    while not user_id:
        try:
            entrada = input("\n🆔 Introduce tu ID de usuario (ej: 1): ")
            if not entrada.isdigit():
                print("⚠️  Por favor, introduce un número.")
                continue
                
            # Llamamos a la función de BBDD que creamos antes
            nombre = validar_usuario(int(entrada))
            
            if nombre:
                user_id = int(entrada)
                nombre_usuario = nombre
                print(f"✅ Login correcto. Hola, {nombre_usuario}.")
            else:
                print("❌ Usuario no encontrado en PostgreSQL. Intenta con otro ID.")
        except KeyboardInterrupt:
            print("\nSalida forzada.")
            return

    # --- PASO 2: CHAT ---
    # Simulamos el bucle de mensajes de la web
    print("\n💬 El sistema está listo. Escribe 'salir' para terminar.")
    print("-" * 40)
    
    while True:
        try:
            texto_usuario = input(f"\n👤 {nombre_usuario}: ")
            
            if texto_usuario.lower() in ['salir', 'exit']:
                print("👋 Cerrando sesión...")
                break
            
            # A) Llamamos al CEREBRO (Services)
            print("   (Pensando...)")
            datos_ia = analizar_duda_con_ia(texto_usuario)
            
            # B) Mostramos la respuesta
            print(f"🤖 CAU: {datos_ia['respuesta']}")
            
            # C) Llamamos a la MEMORIA (DB)
            guardado = registrar_interaccion(user_id, texto_usuario, datos_ia)
            
            # Feedback de depuración (esto no se vería en la web, pero aquí es útil)
            if guardado:
                print(f"   [DEBUG: Guardado en BD | Cat: {datos_ia['categoria']} | Urg: {datos_ia['urgencia']}]")
            else:
                print("   [DEBUG: ❌ Error al guardar en BD]")
                
        except KeyboardInterrupt:
            print("\n👋 Hasta luego.")
            break
        except Exception as e:
            print(f"❌ Error inesperado en el bucle: {e}")

if __name__ == "__main__":
    main()