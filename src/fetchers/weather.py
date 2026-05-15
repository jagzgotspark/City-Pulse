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
