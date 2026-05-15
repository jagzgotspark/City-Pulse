from datetime import datetime

def clean_weather(raw: dict) -> dict:
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "temperature": raw["main"]["temp"],
        "feels_like": raw["main"]["feels_like"],
        "humidity": raw["main"]["humidity"],
        "condition": raw["weather"][0]["main"],
        "wind_speed": raw["wind"]["speed"],
        "visibility": raw.get("visibility", None)
    }

def clean_air_quality(raw: dict) -> dict:
    components = raw["list"][0]["components"]
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "aqi": raw["list"][0]["main"]["aqi"],
        "pm2_5": components.get("pm2_5"),
        "pm10": components.get("pm10"),
        "co": components.get("co")
    }
