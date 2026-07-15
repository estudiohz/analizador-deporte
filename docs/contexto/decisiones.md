# Decisiones técnicas

_Inferidas del código y del historial de commits. Sergio debe validarlas._

## 2026-07-14 · Despliegue como sitio estático en Docker + nginx sobre Dokploy
- **Decisión:** empaquetar la app con un `Dockerfile` multi-stage (Node build → nginx)
  y desplegarla en Dokploy (`deportes.estudiohorizontal.es`, puerto 80, HTTPS Let's Encrypt).
- **Por qué:** la app es 100% estática; nginx la sirve con fallback SPA y cacheo de assets.
- **Descartado:** hosting con backend/Node en runtime (innecesario, no hay servidor).
- **Estado:** vigente. Detalles en [despliegue-dokploy.md](despliegue-dokploy.md).

## 2026-07-14 · Dataset demo integrado en la imagen
- **Decisión:** incluir `demo/data/` (116 actividades sintéticas) y copiarlo a
  `public/data/` durante el build **solo si no hay datos reales**.
- **Por qué:** `public/data/` está gitignored (datos personales), así que un checkout
  limpio no tiene datos. Sin la demo, el panel se vería vacío ("Sin datos aún").
- **Descartado:** subir datos reales al repo (privacidad) · desplegar el panel vacío.
- **Estado:** vigente. Para datos reales, montar un volumen en
  `/usr/share/nginx/html/data` (oculta la demo).

## 2026-06-27 · Arquitectura sin backend: JSON estáticos + descarga local
- **Decisión:** la app lee ficheros JSON de `/data/`; la descarga desde Garmin la hace un
  script Python (`fetch/sync.py`) que corre en local y escribe `public/data/`.
- **Por qué:** datos personales que no deben salir del ordenador; simplicidad (sin infra).
- **Descartado:** backend que hable con la API de Garmin en tiempo real.
- **Estado:** vigente. Es el pilar de toda la arquitectura.

## 2026-06-27 · Métricas de fitness (CTL/ATL/TSB/TSS) calculadas en el cliente
- **Decisión:** el pipeline Python solo entrega resúmenes/detalles/stats; el fitness y la
  estimación de TSS (método TRIMP) se calculan en el navegador (`utils/calculations.ts`).
- **Por qué:** los parámetros del usuario (FTP, maxHR, LTHR) viven en `settings` y deben
  poder recalcular retroactivamente sin re-descargar datos.
- **Descartado:** precalcular el fitness en Python (obligaría a re-sincronizar al cambiar ajustes).
- **Estado:** vigente.

## 2026-06-27 · Estado con zustand, persistiendo solo los ajustes
- **Decisión:** zustand con `persist` sobre localStorage (`garmin-settings`), pero
  `partialize` guarda **solo `settings`**; actividades y stats se re-descargan al arrancar.
- **Por qué:** los datos pueden ser grandes y cambian con cada sync; los ajustes son pequeños
  y deben sobrevivir recargas.
- **Estado:** vigente.
