from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timezone 
from src.scoring.engine import compute_pulse
from src.utils.database import save_pulse_score
import logging

from src.fetchers.weather import fetch_weather
from src.fetchers.air_quality import fetch_air_quality
from src.fetchers.events import fetch_event_density
from src.fetchers.neighbourhood import collect_all_neighbourhoods
from src.utils.transform import clean_weather, clean_air_quality
from src.utils.database import (
    init_db, get_or_create_city,
    save_weather_snapshot, save_air_snapshot, save_city_vector
)
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

CITIES = ["Lucknow", "Mumbai", "Bengaluru", "Delhi"]

def collect_city_data(city_name: str):
    logger.info(f"Starting collection for {city_name}")

    raw_weather = fetch_weather(city_name)
    if raw_weather is None:
        logger.warning(f"Weather fetch failed for {city_name} — skipping")
        return

    lat = raw_weather["coord"]["lat"]
    lon = raw_weather["coord"]["lon"]

    city_id = get_or_create_city(city_name, lat, lon)

    weather_data = clean_weather(raw_weather)
    save_weather_snapshot(city_id, weather_data)
    logger.info(f"Weather saved for {city_name}: {weather_data['temperature']}°C")

    raw_air = fetch_air_quality(lat, lon)
    if raw_air:
        air_data = clean_air_quality(raw_air)
        save_air_snapshot(city_id, air_data)
        logger.info(f"Air quality saved for {city_name}: AQI {air_data['aqi']}")
    else:
        logger.warning(f"Air quality fetch failed for {city_name}")

    events = fetch_event_density(city_name)
    if events:
        logger.info(f"Events for {city_name}: {events['event_count']} active")
    pulse = compute_pulse(
        weather_data,
        air_data if raw_air else {},
        {"event_count": 0}
    )
    pulse["timestamp"] = weather_data["timestamp"]
    pulse["summary"] = f"Pulse score for {city_name}: {pulse['score']}/100"

    save_pulse_score(city_id, pulse)
    logger.info(f"Pulse score for {city_name}: {pulse['score']}/100")    
    save_city_vector({
        "city_name": city_name,
        "timestamp": weather_data["timestamp"],
        "pulse_score": pulse["score"],
        "weather_score": pulse["weather_score"],
        "air_score": pulse["air_score"],
        "temperature": weather_data.get("temperature"),
        "humidity": weather_data.get("humidity"),
        "aqi": air_data.get("aqi") if raw_air else None
    })

def collect_all_cities():
    logger.info(f"=== Collection run started at {datetime.now(timezone.utc)} ===")
    for city in CITIES:
        collect_city_data(city)
    collect_all_neighbourhoods()
    logger.info("=== Collection run complete ===")
    

def run_scheduler():
    """Called from FastAPI startup — runs in a daemon thread."""
    collect_all_cities()
    scheduler = BackgroundScheduler()
    scheduler.add_job(collect_all_cities, "interval", minutes=15)
    scheduler.start()
    logger.info("Background scheduler started")

def start_scheduler():
    """Used when running manually from terminal."""
    init_db()
    scheduler = BlockingScheduler()
    scheduler.add_job(collect_all_cities, "interval", minutes=15)
    collect_all_cities()
    logger.info("Scheduler running — press Ctrl+C to stop")
    scheduler.start()

if __name__ == "__main__":
    start_scheduler()