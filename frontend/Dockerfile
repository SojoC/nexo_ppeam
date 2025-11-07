# frontend/Dockerfile
# Etapa 1: Build con Node (Debian, glibc)
FROM node:20-bullseye-slim AS build
WORKDIR /app

# Ensure devDependencies are installed in the build stage (needed for TypeScript and @types/*)
ENV NODE_ENV=development
COPY package*.json ./
RUN npm ci

# Copiar código y compilar
COPY . .
RUN npm run build

# Etapa 2: Servir con Nginx
FROM nginx:stable-alpine
RUN rm -rf /usr/share/nginx/html/*
# Copy custom nginx config so SPA routes fallback to index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
