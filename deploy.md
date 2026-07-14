# Despliegue — Analizador Deporte en Dokploy

App **estática** (React + Vite) servida por **nginx** dentro de un contenedor Docker.
No tiene backend ni base de datos: la app lee ficheros JSON de `/data/`.

- **Dokploy:** `dokploy.estudiohorizontal.es`
- **Repo:** `estudiohz/analizador-deporte` (rama `main`)
- **Dominio de producción:** `deportes.estudiohorizontal.es`
- **Build:** Dockerfile (multi-stage: Node build → nginx)
- **Puerto del contenedor:** `80`

---

## Datos DEMO

La app muestra un panel de estadísticas de entrenamiento. Los datos reales se
descargarían de Garmin Connect con `fetch/sync.py` a `public/data/`, pero esa
carpeta está en `.gitignore` (contiene datos personales).

Para el despliegue **no se usan datos reales**: el repo incluye un dataset de
demostración sintético en `demo/data/` (116 actividades ficticias en ~7 meses).
El `Dockerfile` lo copia a `public/data/` durante el build **solo si no hay datos
reales**, así el panel se ve poblado.

Regenerar la demo (opcional):

```bash
python3 demo/generate_demo.py   # reescribe demo/data/
```

> Para usar datos reales en su lugar, monta un volumen en
> `/usr/share/nginx/html/data` con tus JSON; eso oculta los datos demo.

---

## Crear el proyecto y la aplicación en Dokploy (web)

1. **Proyecto:** Dashboard → *Create Project* → `Analizador Deporte`.
2. **Aplicación:** dentro del proyecto → *Create Service* → *Application* →
   nombre `analizador-deporte`.
3. **Provider (pestaña General):**
   - Source: **GitHub** (integración ya conectada en Dokploy).
   - Repository: `estudiohz/analizador-deporte`
   - Branch: `main`
   - Build Path: `/`
4. **Build Type:** **Dockerfile** · Dockerfile Path: `Dockerfile`.
5. **Deploy:** botón *Deploy*. Se construye la imagen (npm ci → build → nginx).

---

## Dominio: `deportes.estudiohorizontal.es`

1. **DNS:** crea un registro **A** (o CNAME) para `deportes` en la zona
   `estudiohorizontal.es` apuntando a la **IP pública del servidor Dokploy**
   (la misma a la que resuelve `dokploy.estudiohorizontal.es`).
2. **Dokploy → app → pestaña Domains → Add Domain:**
   - Host: `deportes.estudiohorizontal.es`
   - **Container Port: `80`**
   - Path: `/`
   - **HTTPS: ON** · Certificate: **Let's Encrypt** (Traefik lo emite solo).
3. Guarda y **Deploy/Reload**. En 1-2 min tendrás HTTPS válido.

---

## Autodeploy en cada push (opcional, recomendado)

1. En la app → pestaña **Deployments** → copia la **Webhook URL** de Dokploy.
2. En GitHub `estudiohz/analizador-deporte` → *Settings → Webhooks → Add webhook*:
   - Payload URL: la de Dokploy
   - Content type: `application/json`
   - Events: *Just the push event*
3. A partir de ahí, cada push a `main` redespliega automáticamente.

---

## Comprobación tras el deploy

```bash
curl -I https://deportes.estudiohorizontal.es/                     # 200
curl -s https://deportes.estudiohorizontal.es/data/activities.json | head -c 100   # JSON demo
curl -I https://deportes.estudiohorizontal.es/activities           # 200 (fallback SPA)
```

La app debe cargar mostrando "Analizador Deporte" y el panel con las actividades
demo (no "Sin datos aún").
