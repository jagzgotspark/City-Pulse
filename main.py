from src.fetchers.weather import fetch_weather
from src.fetchers.air_quality import fetch_air_quality
from src.utils.transform import clean_weather, clean_air_quality
from src.utils.database import init_db, get_or_create_city, save_weather_snapshot, save_air_snapshot
from src.scoring.engine import compute_pulse
from src.api.llm import generate_city_summary
from src.utils.database import get_pulse_trend, get_daily_summary, get_city_comparison

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

cities_data = [
    ("Lucknow", {"temperature": 37.99, "condition": "Haze", "aqi": 3, "pulse_score": 29.3}),
    ("Mumbai", {"temperature": 32.99, "condition": "Haze", "aqi": 1, "pulse_score": 67.0}),
    ("Bengaluru", {"temperature": 31.82, "condition": "Clouds", "aqi": 2, "pulse_score": 85.5}),
]

for city_name, data in cities_data:
    summary = generate_city_summary(city_name, data)
    print(f"{city_name}: {summary}")

print("\n=== Pulse Trend (Lucknow) ===")
trend = get_pulse_trend("Lucknow", days=7)
print(f"{len(trend)} hourly data points")
for row in trend[:3]:
    print(row)

print("\n=== City Comparison ===")
comparison = get_city_comparison(days=7)
for row in comparison:
    print(row)