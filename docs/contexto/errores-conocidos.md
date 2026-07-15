# Errores conocidos y gotchas

## El panel aparece vacío / "Sin datos aún"
- **Pasa cuando:** no hay ficheros en `public/data/` (checkout limpio: está gitignored).
- **Causa real:** los datos reales no viajan en el repo por privacidad.
- **Solución:** en local, `cp -r demo/data/. public/data/` o correr `python fetch/sync.py`.
  En el deploy, el `Dockerfile` ya copia la demo automáticamente si `public/data` está vacío.

## Garmin bloquea la cuenta al sincronizar
- **Pasa cuando:** se hacen muchas peticiones seguidas a la API de Garmin.
- **Causa real:** rate limiting agresivo de Garmin Connect.
- **Solución:** `fetch/sync.py` ya mete `time.sleep()` entre actividades y reintentos con
  backoff (`_try`). **No quitar esos sleeps.** Para pruebas, usar `--limit`.

## Los mapas no tienen todos los puntos GPS
- **Pasa cuando:** una actividad tiene miles de trackpoints.
- **Es a propósito:** `fetch_gpx_coords()` submuestrea a ~500 puntos para aligerar el JSON.

## Los números de fitness/TSS "no cuadran" con Garmin
- **Pasa cuando:** Garmin no aporta TSS para una actividad.
- **Causa real:** el TSS se **estima** con TRIMP (`estimateTSS`) usando los ajustes del usuario;
  es una aproximación, no el valor oficial de Garmin.
- **Solución:** ajustar `maxHR`, `ftp`, `lthrRunning` en Ajustes para afinar la estimación.

## Cambiar ajustes recalcula todo el histórico
- **Es a propósito:** `Settings.tsx` avisa de que tocar maxHR/FTP/umbral afecta
  **retroactivamente** a todos los cálculos de CTL/ATL/TSB y zonas. No es un bug.

## Cosas que parecen rotas pero son a propósito
- **No hay backend ni base de datos:** todo es JSON estático. Correcto por diseño.
- **El store solo persiste `settings`:** actividades y stats se re-descargan al arrancar
  (no se guardan en localStorage). Correcto por diseño.
- **`error: dubious ownership` de git** al clonar en `D:\A\...`: es de Windows/permisos, no del
  repo. Solución: `git config --global --add safe.directory 'D:/A/Analizador Deporte'`.
