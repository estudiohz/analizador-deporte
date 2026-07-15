# Despliegue — Dokploy (referencia completa)

App **estática** (React+Vite → nginx en Docker) desplegada en Dokploy.
Estado: **EN PRODUCCIÓN** en https://deportes.estudiohorizontal.es (verificado 200 + HTTPS válido).

## Identificadores (Dokploy)
| Dato | Valor |
|---|---|
| Panel Dokploy | `https://dokploy.estudiohorizontal.es` |
| Proyecto | `analizador-deporte` · projectId **`_uAZhme4WeZNZ19X8ofPh`** |
| Entorno | `production` · environmentId **`j7n9AepoJbfNjzjI-gXDC`** |
| Aplicación | `analizador-deporte` · applicationId **`lq7EmGpGt-KSYH-4SU1yo`** |
| appName interno | `analizador-deporte-lenyof` (autogenerado por Dokploy) |
| Integración GitHub | githubId **`1D1cACSoC83me73VJXGEE`** (`Dokploy-2026-03-27-pf4kfk`) |
| Repo · rama · buildPath | `estudiohz/analizador-deporte` · `main` · `/` |
| Build | **Dockerfile** (`Dockerfile`), multi-stage `npm ci → vite build → nginx` |
| Dominio | `deportes.estudiohorizontal.es` · puerto **80** · HTTPS Let's Encrypt · domainId `05ZCURCLAKucVFSUP6q_7` |
| DNS | registro **A** `deportes` → **195.7.4.21** (IP del servidor Dokploy) |
| Autodeploy | **ON** — cada push a `main` redespliega (`autoDeploy: true`) |

## Servidor de datos
- No hay datos reales en el deploy: el `Dockerfile` copia `demo/data/` → `public/data/`
  durante el build **solo si `public/data` está vacío**.
- Para datos reales: montar un volumen en `/usr/share/nginx/html/data` con los JSON
  (eso oculta la demo).

## Cómo se hizo (API de Dokploy)
Cabecera de auth: `x-api-key: <DK_TOKEN>`. **El token es un secreto — NO se commitea.**
Exportarlo como variable de entorno antes de cualquier llamada:
```bash
export DK_TOKEN="<token-api-de-dokploy>"   # Dokploy → Settings → API/Tokens
export DK_URL="https://dokploy.estudiohorizontal.es"
```
Secuencia usada (todas POST con `Content-Type: application/json`), por si hay que rehacerlo:
1. `application.create` → `{name, appName, description, environmentId}`
2. `application.saveGithubProvider` → `{applicationId, repository, owner, branch, buildPath:"/", githubId, watchPaths:[]}`
3. `application.saveBuildType` → `{applicationId, buildType:"dockerfile", dockerfile:"Dockerfile", herokuVersion:"24", railpackVersion:"0.15.4"}`
   ⚠️ `herokuVersion` y `railpackVersion` son **obligatorios** aunque no se usen (o da 400).
4. `domain.create` → `{host, path:"/", port:80, https:true, applicationId, certificateType:"letsencrypt", domainType:"application"}`
5. `application.deploy` → `{applicationId}`

> El repo trae también `deploy-dokploy.sh`, pero **crea un proyecto nuevo**; aquí el
> proyecto ya existía, así que se usó `environmentId` directamente (no `projectId`).

## Redesplegar / operar
- **Normal:** `git push` a `main` → autodeploy.
- **Manual por API:** `POST /api/application.deploy` con `{"applicationId":"lq7EmGpGt-KSYH-4SU1yo"}`.
- **Estado:** `GET /api/application.one?applicationId=lq7EmGpGt-KSYH-4SU1yo`.
- **Logs y redeploy manual:** panel Dokploy → proyecto `analizador-deporte` → app.

## Verificación post-deploy
```bash
curl -I  https://deportes.estudiohorizontal.es/                       # 200
curl -s  https://deportes.estudiohorizontal.es/data/activities.json | head -c 100   # JSON demo
curl -I  https://deportes.estudiohorizontal.es/activities             # 200 (fallback SPA)
```
