# ---- Build stage ----
FROM node:22-alpine AS build
WORKDIR /app

# Install dependencies (use lockfile for reproducible builds)
COPY package.json package-lock.json ./
RUN npm ci

# Build the static site
COPY . .
RUN npm run build

# ---- Runtime stage ----
FROM nginx:alpine AS runtime

# SPA-aware nginx config (react-router fallback to index.html)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built static assets
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
