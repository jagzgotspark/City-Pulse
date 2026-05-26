def pm25_to_aqi(pm25: float) -> int:
    """Convert PM2.5 concentration to US AQI using EPA formula."""
    if pm25 is None:
        return None

    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]

    for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
        if bp_lo <= pm25 <= bp_hi:
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo
            return round(aqi)

    return 500

def aqi_category(aqi: int) -> dict:
    if aqi is None:
        return {"label": "Unknown", "color": "#94a3b8"}
    if aqi <= 50:
        return {"label": "Good", "color": "#22c55e"}
    if aqi <= 100:
        return {"label": "Moderate", "color": "#f59e0b"}
    if aqi <= 150:
        return {"label": "Unhealthy for Sensitive Groups", "color": "#f97316"}
    if aqi <= 200:
        return {"label": "Unhealthy", "color": "#ef4444"}
    if aqi <= 300:
        return {"label": "Very Unhealthy", "color": "#9333ea"}
    return {"label": "Hazardous", "color": "#7f1d1d"}