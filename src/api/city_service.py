from src.fetchers.weather import fetch_weather, fetch_weather_latlon, geocode_city
from src.fetchers.air_quality import fetch_air_quality
from src.fetchers.events import fetch_event_density
from src.utils.transform import clean_weather, clean_air_quality
from src.utils.database import (
    get_or_create_city,
    save_weather_snapshot,
    save_air_snapshot,
    save_pulse_score,
    get_latest_snapshot,
    get_latest_pulse
)
from src.scoring.engine import compute_pulse

from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def fetch_and_save_city(city_name: str) -> dict | None:
    logger.info(f"On-demand fetch for {city_name}")

    geo = geocode_city(city_name)
    if geo is None:
        logger.warning(f"Geocode failed for {city_name}")
        return None

    lat, lon, actual_name = geo
    raw_weather = fetch_weather_latlon(lat, lon)
    if raw_weather is None:
        logger.warning(f"Weather fetch failed for {city_name}")
        return None

    city_id = get_or_create_city(actual_name, lat, lon)

    weather_data = clean_weather(raw_weather)
    save_weather_snapshot(city_id, weather_data)

    raw_air = fetch_air_quality(lat, lon)
    air_data = {}
    if raw_air:
        air_data = clean_air_quality(raw_air)
        save_air_snapshot(city_id, air_data)

    events = fetch_event_density(actual_name)
    event_count = events["event_count"] if events else 0

    pulse = compute_pulse(weather_data, air_data, {"event_count": event_count})
    pulse["timestamp"] = weather_data["timestamp"]
    pulse["summary"] = f"Pulse score for {actual_name}: {pulse['score']}/100"
    save_pulse_score(city_id, pulse)

    logger.info(f"On-demand fetch complete for {actual_name}: {pulse['score']}/100")

    return {
        "city": actual_name,
        "lat": lat,
        "lon": lon,
        "pulse_score": pulse["score"],
        "weather_score": pulse["weather_score"],
        "air_score": pulse["air_score"],
        "temperature": weather_data["temperature"],
        "condition": weather_data["condition"],
        "aqi": air_data.get("aqi"),
        "timestamp": weather_data["timestamp"]
    }