#!/usr/bin/env python3
"""
Genera un conjunto de datos DEMO para Analizador Deporte.

No usa ninguna cuenta real de Garmin: crea actividades sintéticas y realistas
(running, cycling, swimming) repartidas en ~7 meses, con el mismo formato JSON
que produce fetch/normalizer.py y que consume la app React (ver src/types/garmin.ts).

Salida: demo/data/
  - activities.json            (lista de ActivitySummary)
  - stats.json                 (GlobalStats)
  - activity_<id>.json         (ActivityDetail por actividad)

Determinista (seed fijo) para builds reproducibles.
"""
from __future__ import annotations
import json
import math
import os
import random
from datetime import datetime, timedelta

random.seed(42)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data")
os.makedirs(OUT, exist_ok=True)

# Fecha final del dataset (demo). La app ordena por startTime desc.
END = datetime(2026, 7, 6, 8, 0, 0)

# Punto base para las rutas GPS (parque del Retiro, Madrid) — datos ficticios.
BASE_LAT, BASE_LON = 40.4153, -3.6844

RUN_TITLES = [
    "Rodaje suave", "Series en pista", "Tirada larga", "Fartlek",
    "Tempo run", "Cuestas", "Recuperación", "Progresivo",
]
BIKE_TITLES = [
    "Salida de carretera", "Rodillo Z2", "Intervalos VO2", "Ruta larga",
    "Recuperación activa", "Tempo bici", "Series de umbral",
]
SWIM_TITLES = [
    "Natación técnica", "Series de crol", "Aguas abiertas", "Piscina suave",
]


def gpx_loop(n_points: int, radius_km: float) -> list[list[float]]:
    """Genera una ruta cerrada aproximada como un bucle irregular."""
    coords = []
    dlat = radius_km / 111.0
    dlon = radius_km / (111.0 * math.cos(math.radians(BASE_LAT)))
    for i in range(n_points):
        t = (i / n_points) * 2 * math.pi
        wobble = 0.65 + 0.35 * math.sin(t * 3 + i * 0.15)
        lat = BASE_LAT + math.sin(t) * dlat * wobble
        lon = BASE_LON + math.cos(t) * dlon * wobble
        coords.append([round(lat, 6), round(lon, 6)])
    return coords


def hr_zones(duration: int, avg_hr: int) -> list[dict]:
    """Distribuye el tiempo en 5 zonas de FC de forma plausible."""
    if avg_hr >= 165:
        weights = [0.05, 0.15, 0.30, 0.35, 0.15]
    elif avg_hr >= 150:
        weights = [0.10, 0.30, 0.40, 0.15, 0.05]
    else:
        weights = [0.30, 0.45, 0.20, 0.04, 0.01]
    bounds = [(90, 114), (114, 133), (133, 152), (152, 171), (171, 190)]
    zones = []
    for i, w in enumerate(weights):
        lo, hi = bounds[i]
        zones.append({
            "zone": i + 1,
            "name": f"Zona {i + 1}",
            "seconds": round(duration * w),
            "lowBPM": lo,
            "highBPM": hi,
        })
    return zones


def make_laps(sport: str, distance_km: float, duration: int, avg_hr: int,
              avg_pace, avg_speed, avg_power, elev: int) -> list[dict]:
    laps = []
    if sport == "swimming":
        n = max(1, round(distance_km / 0.1))  # tramos de 100 m
        seg_dist = 0.1
    else:
        n = max(1, round(distance_km))
        seg_dist = distance_km / n if n else distance_km
    seg_dur = duration / n if n else duration
    for i in range(n):
        jitter = random.uniform(0.92, 1.08)
        d = seg_dur * jitter
        lap = {
            "index": i + 1,
            "distance": round(seg_dist, 3),
            "duration": round(d),
            "avgHR": round(avg_hr * random.uniform(0.95, 1.05)) or None,
            "avgPace": round(avg_pace * jitter) if avg_pace else None,
            "avgSpeed": round(avg_speed / jitter, 1) if avg_speed else None,
            "avgPower": round(avg_power * random.uniform(0.9, 1.1)) if avg_power else None,
            "elevationGain": round(elev / n * random.uniform(0.5, 1.5)),
        }
        laps.append(lap)
    return laps


def build():
    activities = []
    details = {}
    vo2_history = []
    day = END
    idx = 0
    base_vo2 = 52.0

    # ~7 meses hacia atrás, 3-4 actividades por semana
    while day > END - timedelta(days=210):
        # nº de sesiones esta semana
        sessions = random.choice([3, 3, 4, 4, 5])
        week_days = sorted(random.sample(range(7), sessions))
        for wd in week_days:
            d = day - timedelta(days=wd)
            if d > END:
                continue
            idx += 1
            aid = 900000000 + idx
            r = random.random()
            if r < 0.55:
                sport = "running"
            elif r < 0.85:
                sport = "cycling"
            else:
                sport = "swimming"

            start = d.replace(hour=random.choice([7, 8, 9, 18, 19]),
                              minute=random.choice([0, 15, 30, 45]))
            start_iso = start.strftime("%Y-%m-%dT%H:%M:%S")

            if sport == "running":
                distance = round(random.uniform(5, 21), 2)
                pace = random.randint(240, 330)  # sec/km
                duration = round(distance * pace)
                avg_hr = random.randint(140, 172)
                max_hr = min(190, avg_hr + random.randint(8, 20))
                elev = random.randint(20, 320)
                summary = {
                    "id": aid, "title": random.choice(RUN_TITLES), "sport": sport,
                    "startTime": start_iso, "distance": distance,
                    "duration": duration, "movingTime": round(duration * 0.98),
                    "elevationGain": elev, "avgHR": avg_hr, "maxHR": max_hr,
                    "calories": round(distance * random.uniform(62, 78)),
                    "tss": round(duration / 3600 * random.uniform(45, 85), 1),
                    "avgPace": pace, "avgSpeed": None, "avgPower": None,
                    "normalizedPower": None,
                    "avgCadence": random.randint(168, 184),
                    "vo2max": round(base_vo2 + random.uniform(-0.5, 0.5), 1),
                    "aerobicTE": round(random.uniform(2.0, 4.2), 1),
                    "anaerobicTE": round(random.uniform(0.2, 2.5), 1),
                }
            elif sport == "cycling":
                distance = round(random.uniform(20, 92), 2)
                speed = round(random.uniform(25, 35), 1)  # km/h
                duration = round(distance / speed * 3600)
                avg_hr = random.randint(125, 162)
                max_hr = min(188, avg_hr + random.randint(10, 25))
                elev = random.randint(120, 900)
                power = random.randint(155, 255)
                summary = {
                    "id": aid, "title": random.choice(BIKE_TITLES), "sport": sport,
                    "startTime": start_iso, "distance": distance,
                    "duration": duration, "movingTime": round(duration * 0.97),
                    "elevationGain": elev, "avgHR": avg_hr, "maxHR": max_hr,
                    "calories": round(duration / 3600 * random.uniform(600, 780)),
                    "tss": round(duration / 3600 * random.uniform(55, 95), 1),
                    "avgPace": None, "avgSpeed": speed,
                    "avgPower": power,
                    "normalizedPower": round(power * random.uniform(1.02, 1.12)),
                    "avgCadence": random.randint(80, 96),
                    "vo2max": round(base_vo2 + random.uniform(-0.5, 0.5), 1),
                    "aerobicTE": round(random.uniform(2.2, 4.0), 1),
                    "anaerobicTE": round(random.uniform(0.3, 2.0), 1),
                }
                pace = None
            else:  # swimming
                distance = round(random.uniform(1.0, 3.2), 2)
                pace = random.randint(900, 1200)  # sec/km
                duration = round(distance * pace)
                avg_hr = random.randint(120, 150)
                max_hr = min(178, avg_hr + random.randint(8, 18))
                elev = 0
                summary = {
                    "id": aid, "title": random.choice(SWIM_TITLES), "sport": sport,
                    "startTime": start_iso, "distance": distance,
                    "duration": duration, "movingTime": duration,
                    "elevationGain": 0, "avgHR": avg_hr, "maxHR": max_hr,
                    "calories": round(distance * random.uniform(180, 240)),
                    "tss": round(duration / 3600 * random.uniform(40, 70), 1),
                    "avgPace": pace, "avgSpeed": None, "avgPower": None,
                    "normalizedPower": None,
                    "avgCadence": random.randint(28, 38),
                    "vo2max": None,
                    "aerobicTE": round(random.uniform(1.8, 3.5), 1),
                    "anaerobicTE": round(random.uniform(0.1, 1.5), 1),
                    "swolf": random.randint(34, 46),
                    "avgStrokesPerLength": round(random.uniform(1.4, 2.2), 2),
                }

            activities.append(summary)

            # Detalle
            detail = dict(summary)
            detail["laps"] = make_laps(
                sport, distance, duration, avg_hr,
                summary.get("avgPace"), summary.get("avgSpeed"),
                summary.get("avgPower"), elev,
            )
            detail["hrZones"] = hr_zones(duration, avg_hr)
            if sport == "swimming":
                detail["gpxCoords"] = []
            else:
                radius = 0.8 + distance * (0.02 if sport == "cycling" else 0.05)
                detail["gpxCoords"] = gpx_loop(max(30, min(400, round(distance * 12))), radius)
            if sport == "running":
                detail["avgStrideLength"] = round(random.uniform(1.05, 1.35), 2)
            detail["trainingEffect"] = summary["aerobicTE"]
            details[aid] = detail

        # progresión de forma: vo2max sube muy lentamente
        base_vo2 = min(58.0, base_vo2 + random.uniform(0.0, 0.25))
        day -= timedelta(days=7)

    # vo2max history (uno cada ~2 semanas, cronológico ascendente)
    runs = [a for a in activities if a["vo2max"] is not None]
    runs.sort(key=lambda a: a["startTime"])
    for a in runs[::6]:
        vo2_history.append({"date": a["startTime"][:10], "value": a["vo2max"]})

    by_type: dict[str, int] = {}
    for a in activities:
        by_type[a["sport"]] = by_type.get(a["sport"], 0) + 1

    stats = {
        "totalActivities": len(activities),
        "byType": by_type,
        "vo2maxHistory": vo2_history,
        "syncedAt": END.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    # Escribir ficheros
    activities.sort(key=lambda a: a["startTime"], reverse=True)
    with open(os.path.join(OUT, "activities.json"), "w", encoding="utf-8") as f:
        json.dump(activities, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(OUT, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, separators=(",", ":"))
    for aid, detail in details.items():
        with open(os.path.join(OUT, f"activity_{aid}.json"), "w", encoding="utf-8") as f:
            json.dump(detail, f, ensure_ascii=False, separators=(",", ":"))

    print(f"Generadas {len(activities)} actividades demo -> {OUT}")
    print(f"  Por tipo: {by_type}")


if __name__ == "__main__":
    build()
