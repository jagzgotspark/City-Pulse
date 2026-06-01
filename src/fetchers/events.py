import requests
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TICKETMASTER_API_KEY")
BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

CITY_COORDS = {
    "Lucknow":    (26.85, 80.95),
    "Mumbai":     (19.08, 72.88),
    "Bengaluru":  (12.97, 77.59),
    "Delhi":      (28.61, 77.23),
}

def fetch_event_density(city: str) -> dict | None:
    if city not in CITY_COORDS:
        print(f"No coordinates for {city}")
        return None

    lat, lon = CITY_COORDS[city]

    try:
        params = {
            "apikey": API_KEY,
            "latlong": f"{lat},{lon}",
            "radius": "50",
            "unit": "km",
            "startDateTime": f"{date.today().strftime('%Y-%m-%d')}T00:00:00Z",
            "size": "1"
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        count = data.get("page", {}).get("totalElements", 0)
        return {"event_count": count}
    except requests.exceptions.Timeout:
        print(f"Events request timed out for {city}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Events HTTP error for {city}: {e}")
        return None
    except Exception as e:
        print(f"Events unexpected error: {e}")
        return None