# Flujo de trabajo

## Antes de tocar nada
- Leer `types/garmin.ts` (el contrato de datos) antes de cambiar nada que toque el JSON.
- Recordar: la app es estática, sin backend. Si un cambio "pide" servidor, es señal de alarma.
- `public/data/` no existe en un checkout limpio (gitignored). Para ver datos hay dos vías:
  correr el pipeline (datos reales) o copiar `demo/data/` a `public/data/`.

## Desarrollo en local
Requisitos: **Node 18+** y (solo para datos reales) **Python 3.10+**.
```bash
npm install
# Opción A — datos demo (rápido, sin Garmin):
cp -r demo/data/. public/data/
# Opción B — datos reales:
cp .env.example .env          # y rellenar GARMIN_EMAIL / GARMIN_PASSWORD
pip install -r fetch/requirements.txt
python fetch/sync.py          # --limit N para probar; --since YYYY-MM-DD; --no-gpx
npm run dev                   # abre Vite en local
```

## Para hacer un cambio
1. Rama desde `main`.
2. Tocar donde corresponda: vista → `pages/`; métrica derivada → `hooks/`; cálculo puro →
   `utils/`; forma del dato → `types/garmin.ts` **y** `fetch/normalizer.py` a la vez.
3. Probar en local con `npm run dev` (con demo o datos reales).

## Antes de dar algo por terminado
- `npm run lint` (oxlint) sin errores.
- `npm run build` compila (`tsc -b && vite build`) sin errores de tipos.
- Si cambió la forma del JSON: verificar que `normalizer.py` y `types/garmin.ts` siguen alineados.
- Actualizar los docs de `docs/contexto/` si cambió arquitectura, convenciones o una decisión.
- No hay tests automáticos: la verificación es manual en el navegador.

## Deploy
- **Autodeploy:** `autoDeploy` está **activo** en Dokploy → cada push a `main` redespliega.
- **Deploy manual / detalles completos (IDs, API, dominio):** ver
  [despliegue-dokploy.md](despliegue-dokploy.md).
- Build en el servidor: `npm ci → vite build → nginx`. Puerto 80, HTTPS Let's Encrypt.
- Comprobación tras deploy:
  ```bash
  curl -I https://deportes.estudiohorizontal.es/                        # 200
  curl -s https://deportes.estudiohorizontal.es/data/activities.json | head -c 100
  curl -I https://deportes.estudiohorizontal.es/activities              # 200 (fallback SPA)
  ```
