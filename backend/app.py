import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.services import analizar_duda_con_ia
from app.db import registrar_interaccion, validar_usuario, obtener_historial

# Inicializamos Flask simple (sin carpetas static)
app = Flask(__name__)

# IMPORTANTE: CORS permite que el Frontend (puerto 80) hable con el Backend (puerto 5000)
CORS(app) 

# --- YA NO NECESITAMOS LA RUTA '/' ---
# El frontend se encargará de mostrar la web.
# Aquí solo dejamos los endpoints /api/...

@app.route('/api/login', methods=['POST'])
def login():
    datos = request.json
    user_id = datos.get('user_id')
    
    nombre = validar_usuario(user_id)
    if nombre:
        return jsonify({"success": True, "user_id": user_id, "nombre": nombre})
    return jsonify({"success": False, "mensaje": "Usuario no encontrado"}), 404

@app.route('/api/chat', methods=['POST'])
def chat():
    datos = request.json
    # print("📢 RECIBIDO:", datos) # Descomenta si quieres depurar
    user_id = datos.get('user_id')
    mensaje = datos.get('mensaje')
    
    if not validar_usuario(user_id):
        return jsonify({"error": "No autorizado"}), 401

    resultado = analizar_duda_con_ia(mensaje, user_id)
    guardado = registrar_interaccion(user_id, mensaje, resultado)
    
    return jsonify({
        "respuesta": resultado["respuesta"],
        "info": {
            "categoria": resultado["categoria"],
            "urgencia": resultado["urgencia"],
            "guardado": guardado
        }
    })

@app.route('/api/consultas', methods=['GET'])
def consultas():
    user_id = request.args.get('user_id')
    categoria = request.args.get('categoria')
    resultados = obtener_historial(user_id, categoria)
    return jsonify(resultados)

if __name__ == '__main__':
    # Mantenemos el host 0.0.0.0 para Docker
    app.run(host='0.0.0.0', port=5000, debug=True)