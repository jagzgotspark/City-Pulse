from datetime import datetime, timezone
from src.fetchers.weather import fetch_weather_latlon, CITY_GRIDS
from src.fetchers.air_quality import fetch_air_quality
from src.utils.transform import clean_weather, clean_air_quality
from src.scoring.engine import compute_pulse
from src.utils.database import save_neighbourhood_snapshot
import logging

logger = logging.getLogger(__name__)

def collect_neighbourhood_data(city_name: str):
    grid = CITY_GRIDS.get(city_name)
    if not grid:
        logger.warning(f"No grid defined for {city_name}")
        return

    for point in grid:
        name = point["name"]
        lat  = point["lat"]
        lon  = point["lon"]

        raw_weather = fetch_weather_latlon(lat, lon)
        if not raw_weather:
            logger.warning(f"Weather failed for {name}, skipping")
            continue

        weather_data = clean_weather(raw_weather)

        raw_air = fetch_air_quality(lat, lon)
        air_data = clean_air_quality(raw_air) if raw_air else {}

        pulse = compute_pulse(weather_data, air_data, {"event_count": 0})

        save_neighbourhood_snapshot({
            "city_name":   city_name,
            "neighbourhood": name,
            "lat":         lat,
            "lon":         lon,
            "timestamp":   datetime.now(timezone.utc),
            "temperature": weather_data.get("temperature"),
            "humidity":    weather_data.get("humidity"),
            "condition":   weather_data.get("condition"),
            "wind_speed":  weather_data.get("wind_speed"),
            "aqi":         air_data.get("aqi"),
            "pm2_5":       air_data.get("pm2_5"),
            "pulse_score": pulse["score"]
        })
        logger.info(f"Saved {name} ({city_name}): pulse {pulse['score']}")


def collect_all_neighbourhoods():
    logger.info("=== Neighbourhood collection started ===")
    for city in CITY_GRIDS.keys():
        collect_neighbourhood_data(city)
    logger.info("=== Neighbourhood collection complete ===")