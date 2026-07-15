# Arquitectura

## En una frase
Panel web personal (SPA) que muestra estadísticas de entrenamiento de Garmin Connect
—actividades, mapas, zonas de FC, fitness CTL/ATL/TSB, récords— leyendo ficheros JSON
estáticos generados desde tu cuenta de Garmin. **No hay servidor ni base de datos.**

## Stack
- **Frontend:** React 19 + Vite 8 + TypeScript, Tailwind CSS 4.
- **Routing:** react-router-dom 7 (SPA con `BrowserRouter`).
- **Estado:** zustand 5 (con `persist`).
- **Gráficas:** recharts 3. **Mapas:** leaflet + react-leaflet 5. **Fechas:** date-fns.
- **Data pipeline (aparte):** Python 3.10+ con `garminconnect` + `python-dotenv`.
- **Lint:** oxlint. **Deploy:** Docker multi-stage (Node build → nginx) en Dokploy.

## Mapa de carpetas
```
src/
  main.tsx              Punto de entrada; monta <App> dentro de <ErrorBoundary>
  App.tsx               Router + carga inicial (loadActivities, loadStats)
  types/garmin.ts       CONTRATO de datos: tipos TS que reflejan el JSON del pipeline
  stores/activityStore.ts  zustand: fetch de /data/*.json + settings persistidos
  pages/                Una vista por ruta (Dashboard, Activities, FitnessChartPage…)
  hooks/                use*.ts: derivan métricas desde el store (memoizados)
  utils/                calculations.ts (CTL/ATL/TSB/TSS), date.ts, formatters.ts
  components/           UI reutilizable (Sidebar, ActivityCard, ActivityMap, badges…)
fetch/                  Pipeline Python: sync.py (descarga) + normalizer.py (transforma)
demo/                   Dataset sintético (116 actividades) + generate_demo.py
public/data/            [gitignored] JSON reales que sirve la app en runtime
Dockerfile · nginx.conf · deploy.md · deploy-dokploy.sh   Despliegue
```

## Flujo de datos
1. **Descarga (local, manual):** `python fetch/sync.py` autentica en Garmin Connect,
   descarga actividades y las normaliza con `normalizer.py` a `public/data/`:
   `activities.json` (lista), `activity_{id}.json` (detalle) y `stats.json` (globales).
2. **Runtime (navegador):** `activityStore` hace `fetch('/data/activities.json')` etc.
   al montar. Los detalles se cargan bajo demanda y se cachean en memoria (`detailCache`).
3. **Cálculo en cliente:** las métricas de fitness (CTL/ATL/TSB) y la estimación de TSS
   se calculan en el navegador en `utils/calculations.ts`, **no** en el Python.

## Lo que NO existe
- **Sin backend ni API propia** — solo ficheros JSON estáticos servidos por nginx.
- **Sin base de datos.** El único estado persistido es `settings` en localStorage.
- **Sin tests** (unitarios ni e2e) y **sin CI**.
- **Sin autenticación** en la app web (los datos de Garmin se descargan aparte, en local).
- Los datos reales (`public/data/`) **no viajan en el repo** (gitignored por privacidad).
