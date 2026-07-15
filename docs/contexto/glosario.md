# Glosario y entidades

## Términos del dominio
- **TSS** (Training Stress Score): carga de una sesión. Si Garmin no la da, se **estima**
  con método TRIMP en `estimateTSS()` (`utils/calculations.ts`).
- **CTL** (Chronic Training Load / *Fitness*): media móvil exponencial de 42 días del TSS diario.
- **ATL** (Acute Training Load / *Fatigue*): EMA de 7 días del TSS diario.
- **TSB** (Training Stress Balance / *Form*): `CTL − ATL`. Positivo = fresco; negativo = fatigado.
- **TRIMP** (Training Impulse): modelo carga=f(duración, %reserva de FC); base de la estimación de TSS.
- **FTP** (Functional Threshold Power): vatios sostenibles ~1h (ciclismo). Ajuste de usuario.
- **LTHR** (Lactate Threshold HR): FC de umbral (carrera). Ajuste de usuario (`lthrRunning`).
- **VO2max**: consumo máximo de oxígeno; historial en `stats.json`.
- **TE** (Training Effect): efecto aeróbico/anaeróbico de la sesión (`aerobicTE`, `anaerobicTE`).
- **NP** (Normalized Power): potencia normalizada (ciclismo).
- **Pace / ritmo:** segundos por km (running/swim). **Speed:** km/h (ciclismo).
- **SWOLF:** eficiencia en natación (brazadas + tiempo por largo).
- **HR zones:** reparto de tiempo por zona de frecuencia cardíaca.

## Entidades principales
_Definidas en `src/types/garmin.ts` (contrato con el pipeline Python)._
- **ActivitySummary:** fila ligera de la lista de actividades (`activities.json`).
- **ActivityDetail:** extiende Summary con `laps`, `hrZones`, `gpxCoords` (`activity_{id}.json`).
- **FitnessPoint:** punto diario `{ date, ctl, atl, tsb, tss }` (calculado en cliente).
- **GlobalStats:** totales, conteo por tipo, historial de VO2max, `syncedAt` (`stats.json`).
- **UserSettings:** `maxHR`, `ftp`, `lthrRunning`, `thresholdPace` (persistido en localStorage).
- **HRZone / Lap:** zona de FC y vuelta/split individual dentro de un detalle.

## Siglas y nombres internos
- **`garmin-settings`:** clave de localStorage donde zustand persiste los ajustes.
- **`detailCache`:** caché en memoria de detalles ya descargados (en el store).
- **`SPORT_MAP`** (`normalizer.py`): mapea tipos de Garmin a `running|cycling|swimming|other`.
- **demo:** dataset sintético de `demo/data/` usado cuando no hay datos reales.
