# Convenciones

## Estilo
- **TypeScript** con reglas estrictas activas en `tsconfig.app.json`: `noUnusedLocals`,
  `noUnusedParameters`, `noFallthroughCasesInSwitch`, `verbatimModuleSyntax`.
  → Por `verbatimModuleSyntax`, importa tipos con `import type { X } from '...'`.
- **Linter:** oxlint (`npm run lint`). Regla dura: `react/rules-of-hooks: error`.
- **Idiomas:** identificadores de código en **inglés**; textos de UI y comentarios
  de dominio en **español**. Mantener ese patrón (no traducir la UI a inglés).
- **Nombres de fichero:** componentes y páginas en `PascalCase.tsx`; hooks y utils en
  `camelCase.ts`; hooks siempre con prefijo `use*`.

## Patrones que SÍ usamos
- **Store zustand con selectores:** `useActivityStore(s => s.activities)` — seleccionar
  solo lo necesario, no el store entero. Ver `stores/activityStore.ts`.
- **Hooks derivados memoizados:** cada `hooks/use*.ts` toma datos del store y calcula una
  vista con `useMemo`. Ejemplo canónico: `hooks/useFitnessHistory.ts`.
- **Cálculo puro en `utils/`:** funciones sin estado, testeables a mano
  (`calculations.ts` → `estimateTSS`, `calculateFitnessHistory`).
- **`types/garmin.ts` es el contrato único** entre el pipeline Python y el front:
  si cambias la forma del JSON, cambia aquí primero. `normalizer.py` debe reflejarlo.
- **Carga perezosa + caché:** detalles de actividad vía `loadDetail(id)` con `detailCache`.
- **Python:** type hints (`from __future__ import annotations`), helper `_try()` con
  reintentos y `time.sleep()` para no saturar Garmin.

## Patrones PROHIBIDOS
- **No añadir backend, API ni base de datos** — el proyecto es estático por diseño.
- **No persistir datos de actividad** en el store (solo `settings`); se re-descargan.
- **No hacer login a Garmin desde el navegador** — eso vive solo en `fetch/` (local).
- **No subir `public/data/` ni `.env`** (datos personales / credenciales). Ya en `.gitignore`.
- No usar `import` normal para tipos (rompe con `verbatimModuleSyntax`).

## Tests
- **No hay framework de tests.** No hay carpeta de tests ni scripts de test.
  [PENDIENTE: si se añaden tests, definir framework —p. ej. Vitest— y ubicación].

## Commits
- Mensajes en **español**, descriptivos. Conviven dos formatos en el historial:
  imperativo llano ("Añadir…", "Renombrar…") y Conventional Commits ("feat: …").
  [PENDIENTE: elegir uno y unificar si se quiere consistencia].
