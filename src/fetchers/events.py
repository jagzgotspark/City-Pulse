import requests
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("PREDICTHQ_TOKEN")
BASE_URL = "https://api.predicthq.com/v1/events/"

CITY_COORDS = {
    "Lucknow": (26.85, 80.95),
    "Mumbai": (19.08, 72.88),
    "Bengaluru": (12.97, 77.59)
}

def fetch_event_density(city: str) -> dict | None:
    if city not in CITY_COORDS:
        print(f"No coordinates for {city}")
        return None

    lat, lon = CITY_COORDS[city]

    try:
        headers = {"Authorization": f"Bearer {TOKEN}"}
        params = {
            "within": f"50km@{lat},{lon}",
            "active.gte": date.today().strftime("%Y-%m-%d"),
            "limit": "1"
        }
        response = requests.get(
            BASE_URL,
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return {
            "event_count": data.get("count", 0)
        }
    except requests.exceptions.Timeout:
        print(f"Events request timed out for {city}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Events HTTP error for {city}: {e}")
        return None
    except Exception as e:
        print(f"Events unexpected error: {e}")
        return None