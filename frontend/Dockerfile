# frontend/Dockerfile
# Etapa 1: Construcción del proyecto (build)
FROM node:20-alpine AS build

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivos necesarios
COPY package*.json ./
RUN npm ci --only=production

# Copiar el resto del código y compilar
COPY . .
RUN npm run build

# Etapa 2: Servidor liviano para archivos estáticos
FROM nginx:stable-alpine

# Elimina configuración por defecto y copia la tuya
RUN rm -rf /usr/share/nginx/html/*

# Copia el resultado del build a la carpeta pública de nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Expone el puerto 80
EXPOSE 80

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]
