# ---- Build stage ----
FROM node:22-alpine AS build
WORKDIR /app

# Install dependencies (use lockfile for reproducible builds)
COPY package.json package-lock.json ./
RUN npm ci

# Build the static site
COPY . .

# Datos DEMO: si no hay datos reales en public/data, usa el dataset de demostración.
# (public/data/ está en .gitignore para proteger datos personales, así que en el
#  repo solo viaja demo/data/. En un despliegue con datos reales, monta un volumen
#  en /usr/share/nginx/html/data y estos datos demo quedan ocultos.)
RUN mkdir -p public/data && \
    if [ -z "$(ls -A public/data 2>/dev/null)" ] && [ -d demo/data ]; then \
      cp -r demo/data/. public/data/ && echo "Usando datos DEMO"; \
    fi

RUN npm run build

# ---- Runtime stage ----
FROM nginx:alpine AS runtime

# SPA-aware nginx config (react-router fallback to index.html)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built static assets
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
