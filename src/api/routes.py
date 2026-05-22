from fastapi import APIRouter, HTTPException
from src.api.llm import generate_city_summary
from src.api.cache import get_cached, set_cached
from src.api.city_service import fetch_and_save_city

from src.utils.database import (
    get_all_cities,
    get_latest_snapshot,
    get_latest_pulse,
    get_history,
    get_pulse_trend,
    get_daily_summary,
    get_city_comparison
)
from src.api.models import (
    PulseResponse, HistoryResponse, DashboardResponse
)
from fastapi import APIRouter, HTTPException, Query

import logging
logger = logging.getLogger(__name__)

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

@router.get("/search/{city_name}")
def search_city(city_name: str):
    # First check if we already have recent data
    snapshot = get_latest_snapshot(city_name)
    pulse = get_latest_pulse(city_name)

    if snapshot and pulse:
        logger.info(f"Returning cached data for {city_name}")
        return {
            "city": city_name,
            "lat": None,
            "lon": None,
            "pulse_score": pulse["score"],
            "temperature": snapshot["temperature"],
            "condition": snapshot["condition"],
            "aqi": snapshot["aqi"],
            "source": "cache"
        }

    # Not in DB — fetch fresh
    result = fetch_and_save_city(city_name)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find city: {city_name}. Check spelling and try again."
        )

    result["source"] = "fresh"
    return result
@router.get("/trend/{city_name}")
def get_trend(city_name: str, days: int = Query(default=7, ge=1, le=30)):
    trend = get_pulse_trend(city_name, days=days)
    if not trend:
        raise HTTPException(
            status_code=404,
            detail=f"No trend data for {city_name} yet — keep the scheduler running."
        )
    return {
        "city": city_name,
        "days": days,
        "data_points": len(trend),
        "trend": trend
    }

@router.get("/daily/{city_name}")
def get_daily(city_name: str, days: int = Query(default=30, ge=1, le=90)):
    daily = get_daily_summary(city_name, days=days)
    return {
        "city": city_name,
        "days": days,
        "daily": daily
    }

@router.get("/comparison")
def get_comparison(days: int = Query(default=7, ge=1, le=30)):
    comparison = get_city_comparison(days=days)
    return {
        "days": days,
        "cities": comparison
    }
