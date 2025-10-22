# frontend/Dockerfile
# Etapa 1: Build con Node (Debian, glibc)
FROM node:20-bullseye-slim AS build
WORKDIR /app

# Instalar TODAS las deps (incluye devDependencies para Vite/TS/Rolldown)
COPY package*.json ./
RUN npm ci

# Copiar código y compilar
COPY . .
RUN npm run build

# Etapa 2: Servir con Nginx
FROM nginx:stable-alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
