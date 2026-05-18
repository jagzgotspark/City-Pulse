from fastapi import APIRouter, HTTPException
from src.api.llm import generate_city_summary
from src.api.cache import get_cached, set_cached

from src.utils.database import (
    get_all_cities,
    get_latest_snapshot,
    get_latest_pulse,
    get_history
)
from src.api.models import (
    PulseResponse, HistoryResponse, DashboardResponse
)
from fastapi import APIRouter, HTTPException, Query


router = APIRouter()

@router.get("/cities")
def get_cities():
    cities = get_all_cities()
    if not cities:
        raise HTTPException(status_code=404, detail="No cities found")
    return {"cities": cities}

@router.get("/pulse/{city_name}",response_model=PulseResponse)
def get_pulse(city_name: str):
    snapshot = get_latest_snapshot(city_name)
    pulse = get_latest_pulse(city_name)

    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for {city_name}"
        )

    return {
        "city": city_name,
        "temperature": snapshot["temperature"],
        "humidity": snapshot["humidity"],
        "condition": snapshot["condition"],
        "aqi": snapshot["aqi"],
        "pulse_score": pulse["score"] if pulse else None,
        "weather_score": pulse["weather_score"] if pulse else None,
        "air_score": pulse["air_score"] if pulse else None,
        "timestamp": snapshot["timestamp"]
    }

@router.get("/history/{city_name}")
def get_city_history(
    city_name: str,
    hours: int = Query(default=24, ge=1, le=168)
):
    history = get_history(city_name, hours=hours)
    if not history:
        raise HTTPException(status_code=404, detail=f"No history found")
    return {"city": city_name, "hours": hours, "snapshots": history}

@router.get("/dashboard")
def get_dashboard():
    cities = get_all_cities()
    result = []
    for city in cities:
        pulse = get_latest_pulse(city["name"])
        snapshot = get_latest_snapshot(city["name"])
        if pulse and snapshot:
            data = {
                "temperature": snapshot["temperature"],
                "condition": snapshot["condition"],
                "aqi": snapshot["aqi"],
                "pulse_score": pulse["score"]
            }
            cached = get_cached(f"summary_{city['name']}")
            if cached:
                summary = cached
            else:
                summary = generate_city_summary(city["name"], data)
                set_cached(f"summary_{city['name']}", summary)

            result.append({
                "city": city["name"],
                "lat": city["lat"],
                "lon": city["lon"],
                "pulse_score": pulse["score"],
                "temperature": snapshot["temperature"],
                "condition": snapshot["condition"],
                "aqi": snapshot["aqi"],
                "summary": summary
            })
    return {"cities": result}

@router.get("/summary/{city_name}")
def get_city_summary(city_name: str):
    cached = get_cached(f"summary_{city_name}")
    if cached:
        return {"city": city_name, "summary": cached, "cached": True}

    snapshot = get_latest_snapshot(city_name)
    pulse = get_latest_pulse(city_name)

    if not snapshot:
        raise HTTPException(status_code=404, detail=f"No data for {city_name}")

    data = {
        "temperature": snapshot["temperature"],
        "condition": snapshot["condition"],
        "aqi": snapshot["aqi"],
        "pulse_score": pulse["score"] if pulse else 50
    }

    summary = generate_city_summary(city_name, data)
    set_cached(f"summary_{city_name}", summary)
    return {"city": city_name, "summary": summary, "cached": False}