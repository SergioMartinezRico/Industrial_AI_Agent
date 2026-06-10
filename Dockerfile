# Utilizar una imagen base ligera de Python
FROM python:3.10-slim

# Instalar Nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias del backend e instalarlas
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY backend /app/backend

# Copiar los archivos estáticos del frontend a la ruta por defecto de Nginx
COPY frontend /usr/share/nginx/html

# Copiar nuestro archivo de configuración de Nginx modificado
COPY nginx.conf /etc/nginx/nginx.conf

# Dar permisos necesarios a Nginx para entornos contenerizados
RUN chmod -R 777 /var/log/nginx /var/lib/nginx /run

# Exponer el puerto 7860 exigido por Hugging Face
EXPOSE 7860

# Comando para iniciar Nginx en segundo plano y Flask en primer plano
# Se establece el PYTHONPATH para evitar errores de importación en el backend
ENV PYTHONPATH=/app/backend
CMD nginx && python backend/app.py