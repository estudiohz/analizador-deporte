#!/usr/bin/env bash
#
# Despliega "Analizador Deporte" en Dokploy vía API.
# Uso:
#   export DK_TOKEN="<tu-api-token-de-dokploy>"
#   ./deploy-dokploy.sh
#
# Requisitos: bash, curl y python3 (para parsear JSON).
#
set -euo pipefail

# ----- Configuración -----
DK_URL="${DK_URL:-https://dokploy.estudiohorizontal.es}"
PROJECT_NAME="Analizador Deporte"
APP_NAME="analizador-deporte"          # nombre interno (sin espacios)
REPO_OWNER="estudiohz"
REPO_NAME="analizador-deporte"
BRANCH="main"
DOMAIN="deportes.estudiohorizontal.es"
CONTAINER_PORT=80

: "${DK_TOKEN:?Define DK_TOKEN con tu API token de Dokploy}"

H_AUTH=(-H "x-api-key: ${DK_TOKEN}" -H "Content-Type: application/json")
api() { curl -sS "${H_AUTH[@]}" "$@"; }
jqp() { python3 -c "import sys,json;d=json.load(sys.stdin);print($1)"; }

echo "==> 1/6  Comprobando conexión…"
api "${DK_URL}/api/project.all" >/dev/null && echo "    OK"

echo "==> 2/6  Localizando la integración de GitHub (githubId)…"
GITHUB_ID=$(api "${DK_URL}/api/github.githubProviders" \
  | jqp "d[0].get('githubId') if isinstance(d,list) and d else ''" || true)
if [ -z "${GITHUB_ID:-}" ]; then
  echo "    ⚠ No pude leer githubId automáticamente."
  echo "      Abre ${DK_URL}/swagger, busca el endpoint de GitHub providers"
  echo "      y exporta:  export GITHUB_ID=xxxxx   (y vuelve a lanzar el script)."
  : "${GITHUB_ID:?Falta GITHUB_ID}"
fi
echo "    githubId = ${GITHUB_ID}"

echo "==> 3/6  Creando proyecto \"${PROJECT_NAME}\"…"
PROJECT_ID=$(api -X POST "${DK_URL}/api/project.create" \
  -d "$(python3 -c 'import json,os;print(json.dumps({"name":os.environ["PROJECT_NAME"],"description":"Panel de estadísticas deportivas (demo)"}))' PROJECT_NAME="$PROJECT_NAME")" \
  | jqp "d.get('projectId') or d.get('id')")
echo "    projectId = ${PROJECT_ID}"

echo "==> 4/6  Creando aplicación \"${APP_NAME}\"…"
APP_ID=$(api -X POST "${DK_URL}/api/application.create" \
  -d "$(python3 -c 'import json,os;print(json.dumps({"name":os.environ["APP_NAME"],"appName":os.environ["APP_NAME"],"description":"React + Vite (nginx)","projectId":os.environ["PROJECT_ID"]}))' APP_NAME="$APP_NAME" PROJECT_ID="$PROJECT_ID")" \
  | jqp "d.get('applicationId') or d.get('id')")
echo "    applicationId = ${APP_ID}"

echo "==> 5/6  Conectando repo GitHub + build por Dockerfile…"
api -X POST "${DK_URL}/api/application.saveGithubProvider" \
  -d "$(python3 -c 'import json,os;print(json.dumps({"applicationId":os.environ["APP_ID"],"repository":os.environ["REPO_NAME"],"owner":os.environ["REPO_OWNER"],"branch":os.environ["BRANCH"],"buildPath":"/","githubId":os.environ["GITHUB_ID"]}))' APP_ID="$APP_ID" REPO_NAME="$REPO_NAME" REPO_OWNER="$REPO_OWNER" BRANCH="$BRANCH" GITHUB_ID="$GITHUB_ID")" >/dev/null

api -X POST "${DK_URL}/api/application.saveBuildType" \
  -d "$(python3 -c 'import json,os;print(json.dumps({"applicationId":os.environ["APP_ID"],"buildType":"dockerfile","dockerfile":"Dockerfile","dockerContextPath":"","dockerBuildStage":""}))' APP_ID="$APP_ID")" >/dev/null

echo "    Añadiendo dominio ${DOMAIN} (HTTPS Let's Encrypt)…"
api -X POST "${DK_URL}/api/domain.create" \
  -d "$(python3 -c 'import json,os;print(json.dumps({"host":os.environ["DOMAIN"],"path":"/","port":int(os.environ["PORT"]),"https":True,"applicationId":os.environ["APP_ID"],"certificateType":"letsencrypt","domainType":"application"}))' DOMAIN="$DOMAIN" PORT="$CONTAINER_PORT" APP_ID="$APP_ID")" >/dev/null

echo "==> 6/6  Lanzando deploy…"
api -X POST "${DK_URL}/api/application.deploy" \
  -d "$(python3 -c 'import json,os;print(json.dumps({"applicationId":os.environ["APP_ID"]}))' APP_ID="$APP_ID")" >/dev/null

echo ""
echo "✅ Listo. Sigue el build en:  ${DK_URL}  → proyecto \"${PROJECT_NAME}\""
echo "   Cuando termine:  https://${DOMAIN}"
echo ""
echo "   Recuerda el DNS: registro A de 'deportes' -> IP del servidor Dokploy."
