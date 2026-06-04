from fastapi import APIRouter, HTTPException
from src.api.llm import generate_city_summary
from src.api.cache import get_cached, set_cached
from src.api.city_service import fetch_and_save_city
from src.ml.forecast import forecast_city
from src.ml.similarity import get_similar_cities
from src.utils.database import (
    get_all_cities,
    get_latest_snapshot,
    get_latest_pulse,
    get_history,
    get_pulse_trend,
    get_daily_summary,
    get_city_comparison,
    get_neighbourhood_data 
)
from src.api.models import (
    PulseResponse, HistoryResponse, DashboardResponse
)
from fastapi import APIRouter, HTTPException, Query
from src.utils.aqi import pm25_to_aqi, aqi_category
from sqlalchemy import text
from src.utils.database import engine


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

            # Real AQI from PM2.5
            with engine.connect() as conn:
                air_result = conn.execute(text("""
                    SELECT pm2_5 FROM air_quality_snapshots a
                    JOIN cities c ON a.city_id = c.id
                    WHERE c.name = :city_name
                    ORDER BY a.timestamp DESC
                    LIMIT 1
                """), {"city_name": city["name"]})
                air_row = air_result.fetchone()
                pm25 = air_row[0] if air_row else None
            real_aqi = pm25_to_aqi(pm25)
            aqi_info = aqi_category(real_aqi)

            result.append({
                "city": city["name"],
                "lat": city["lat"],
                "lon": city["lon"],
                "pulse_score": pulse["score"],
                "temperature": snapshot["temperature"],
                "condition": snapshot["condition"],
                "aqi": snapshot["aqi"],
                "real_aqi": real_aqi,
                "aqi_label": aqi_info["label"],
                "aqi_color": aqi_info["color"],
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
        city_meta = next((c for c in get_all_cities() if c["name"] == city_name), {})
        return {
            "city": city_name,
            "lat": city_meta.get("lat"),
            "lon": city_meta.get("lon"),

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

@router.get("/forecast/{city_name}")
def get_forecast(city_name: str):
    cached = get_cached(f"forecast_{city_name}")
    if cached:
        return {**cached, "cached": True}

    result = forecast_city(city_name, hours_ahead=24)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Not enough data to forecast {city_name}. Need at least 10 data points."
        )

    set_cached(f"forecast_{city_name}", result)
    return {**result, "cached": False}

@router.get("/forecast")
def get_all_forecasts():
    cities = ["Lucknow", "Mumbai", "Bengaluru"]
    results = []
    for city in cities:
        cached = get_cached(f"forecast_{city}")
        if cached:
            results.append({**cached, "cached": True})
            continue
        result = forecast_city(city, hours_ahead=24)
        if result:
            set_cached(f"forecast_{city}", result)
            results.append({**result, "cached": False})
    return {"forecasts": results}

@router.get("/neighbourhood/{city_name}")
def get_neighbourhood(city_name: str):
    data = get_neighbourhood_data(city_name)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No neighbourhood data for {city_name} yet — wait for next scheduler run."
        )
    return {
        "city": city_name,
        "neighbourhoods": data
    }

@router.get("/similar/{city_name}")
def get_similar(city_name: str):
    results = get_similar_cities(city_name)
    if results is None:
        raise HTTPException(
            status_code=404,
            detail=f"Not enough city data to compute similarity for {city_name}."
        )
    return {"city": city_name, "similar": results}