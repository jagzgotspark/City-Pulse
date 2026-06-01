import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def fetch_weather(city: str)->dict | None:
    try:
        params={
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }
        response=requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Request timed out for {city}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for {city}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"

def geocode_city(city: str) -> tuple | None:
    """Returns (lat, lon, actual_name) for the best India match."""
    try:
        params = {
            "q": f"{city},IN",
            "limit": 5,
            "appid": API_KEY
        }
        response = requests.get(GEOCODE_URL, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()
        if not results:
            # fallback — try without country code
            params["q"] = city
            response = requests.get(GEOCODE_URL, params=params, timeout=10)
            results = response.json()
        if not results:
            return None
        top = results[0]
        return (top["lat"], top["lon"], top.get("name", city))
    except Exception as e:
        print(f"Geocode error for {city}: {e}")
        return None

CITY_GRIDS = {
    "Lucknow": [
        {"name": "Hazratganj",   "lat": 26.8467, "lon": 80.9462},
        {"name": "Gomti Nagar",  "lat": 26.8469, "lon": 81.0010},
        {"name": "Aliganj",      "lat": 26.8762, "lon": 80.9990},
        {"name": "Chowk",        "lat": 26.8600, "lon": 80.9197},
        {"name": "Indira Nagar", "lat": 26.8735, "lon": 81.0050},
        {"name": "Alambagh",     "lat": 26.8080, "lon": 80.9113},
    ],
    "Mumbai": [
        {"name": "Bandra",       "lat": 19.0596, "lon": 72.8295},
        {"name": "Andheri",      "lat": 19.1136, "lon": 72.8697},
        {"name": "Colaba",       "lat": 18.9067, "lon": 72.8147},
        {"name": "Dadar",        "lat": 19.0178, "lon": 72.8478},
        {"name": "Borivali",     "lat": 19.2307, "lon": 72.8567},
        {"name": "Kurla",        "lat": 19.0726, "lon": 72.8795},
    ],
    "Bengaluru": [
        {"name": "Koramangala",    "lat": 12.9352, "lon": 77.6245},
        {"name": "Indiranagar",    "lat": 12.9716, "lon": 77.6412},
        {"name": "Whitefield",     "lat": 12.9698, "lon": 77.7499},
        {"name": "Jayanagar",      "lat": 12.9308, "lon": 77.5839},
        {"name": "Hebbal",         "lat": 13.0350, "lon": 77.5970},
        {"name": "Electronic City","lat": 12.8399, "lon": 77.6770},
    ],
    "Delhi": [
        {"name": "Connaught Place", "lat": 28.6315, "lon": 77.2167},
        {"name": "Dwarka",          "lat": 28.5921, "lon": 77.0460},
        {"name": "Rohini",          "lat": 28.7041, "lon": 77.1025},
        {"name": "Saket",           "lat": 28.5244, "lon": 77.2066},
        {"name": "Lajpat Nagar",    "lat": 28.5677, "lon": 77.2433},
        {"name": "Karol Bagh",      "lat": 28.6520, "lon": 77.1906},
    ],
}


def fetch_weather_latlon(lat: float, lon: float) -> dict | None:
    try:
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Request timed out for ({lat}, {lon})")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for ({lat}, {lon}): {e}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching ({lat}, {lon}): {e}")
        return None