# Usamos una imagen ligera de Nginx
FROM nginx:alpine

# Copiamos tus archivos HTML/JS al directorio público de Nginx
# El punto (.) significa "la carpeta actual frontend"
COPY . /usr/share/nginx/html

# Exponemos el puerto 80 (el estándar para webs)
EXPOSE 80