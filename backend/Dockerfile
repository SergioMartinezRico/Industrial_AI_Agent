# 1. Usamos una imagen base de Python ligera (versión 3.10)
FROM python:3.10-slim

# 2. Evitamos que Python genere archivos .pyc y forzamos logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Creamos la carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiamos primero los requisitos (para aprovechar la caché de Docker)
COPY requirements.txt .

# 5. Instalamos las librerías
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos TODO el código del proyecto (app.py, services.py, frontend/, etc.)
COPY . .

# 7. Exponemos el puerto 5000 (el de Flask)
EXPOSE 5000

# 8. Comando para arrancar la aplicación
# Usamos el modo simple compatible con tu código actual
CMD ["python", "app.py"]