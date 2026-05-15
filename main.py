from src.fetchers.weather import fetch_weather
from src.fetchers.air_quality import fetch_air_quality
from src.utils.transform import clean_weather, clean_air_quality
from src.utils.database import init_db, get_or_create_city, save_weather_snapshot, save_air_snapshot
from src.scoring.engine import compute_pulse

init_db()

cities_to_track = ["Lucknow", "Mumbai", "Bengaluru"]

for city_name in cities_to_track:
    print(f"\nProcessing {city_name}...")

    raw_weather = fetch_weather(city_name)
    if raw_weather is None:
        print(f"Skipping {city_name}")
        continue

    lat = raw_weather["coord"]["lat"]
    lon = raw_weather["coord"]["lon"]

    city_id = get_or_create_city(city_name, lat, lon)

    weather_data = clean_weather(raw_weather)
    save_weather_snapshot(city_id, weather_data)

    raw_air = fetch_air_quality(lat, lon)
    air_data = {}
    if raw_air:
        air_data = clean_air_quality(raw_air)
        save_air_snapshot(city_id, air_data)

    pulse = compute_pulse(weather_data, air_data, {"event_count": 0})
    print(f"{city_name} pulse score: {pulse}")