# Analizador Deporte

Panel web personal (SPA React + Vite) para ver estadísticas de entrenamiento de Garmin
Connect. **Sin backend ni base de datos:** lee ficheros JSON estáticos de `/data/`,
generados en local por un pipeline Python (`fetch/`). Desplegado en Dokploy como sitio
estático (Docker + nginx) en **https://deportes.estudiohorizontal.es**.

## 📚 Contexto del proyecto
Lee estos documentos antes de trabajar:
- @docs/contexto/arquitectura.md
- @docs/contexto/convenciones.md
- @docs/contexto/decisiones.md
- @docs/contexto/glosario.md
- @docs/contexto/flujo-de-trabajo.md
- @docs/contexto/errores-conocidos.md
- @docs/contexto/despliegue-dokploy.md

## Reglas rápidas
- Es una app **estática por diseño**: no añadir backend, API ni base de datos.
- `types/garmin.ts` es el contrato de datos; si cambia el JSON, cambia también `fetch/normalizer.py`.
- No subir nunca `public/data/` ni `.env` (datos personales / credenciales de Garmin).
- Verificar con `npm run lint` y `npm run build` antes de dar algo por terminado (no hay tests).
- Deploy: push a `main` → autodeploy en Dokploy. Detalles e IDs en `docs/contexto/despliegue-dokploy.md`.
