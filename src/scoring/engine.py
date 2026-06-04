"""
City Pulse Scoring Engine
=========================
Computes a pulse score (0-100) for a city based on:

- Weather (weight: X): Scores temperature comfort, humidity,
  wind, and sky condition. Ideal temp range: 22-28C for Indian cities.

- Air Quality (weight: X): Maps OpenWeatherMap AQI (1-5) to 0-100.
  AQI 5 is a hard cap — heavily penalises the final score.

- Events (weight: X): More active events = higher city energy.
  Baseline is 0 events = 40 points (neutral, not zero).

Weights sum to 1.0. Scores are clamped to [0, 100].
"""

_weights = {
    "weather": 0.50,
    "air": 0.35,
    "events": 0.15
}

def get_weights() -> dict:
    return dict(_weights)

def set_weights(weather: float, air: float, events: float):
    total = weather + air + events
    if abs(total - 1.0) > 0.01:
        raise ValueError(f"Weights must sum to 1.0, got {total}")
    _weights["weather"] = round(weather, 2)
    _weights["air"] = round(air, 2)
    _weights["events"] = round(events, 2)


def score_weather(
    temperature: float,
    humidity: int,
    condition: str,
    wind_speed: float
) -> float:

    score = 100.0

    # -----------------------------
    # TEMPERATURE LOGIC
    # -----------------------------

    if 24 <= temperature <= 27:
        pass  # perfect range

    elif 28 <= temperature <= 31:
        score -= (temperature - 27) * 5

    elif 32 <= temperature <= 36:
        score -= 20 + ((temperature - 31) * 8)

    elif temperature > 36:
        score -= 60 + ((temperature - 36) * 10)

    elif temperature < 24:
        score -= (24 - temperature) * 3

    # -----------------------------
    # HUMIDITY LOGIC
    # -----------------------------

    # humidity mostly becomes painful
    # when combined with heat

    if temperature > 30:

        if humidity >= 75:
            score -= 15

        if humidity >= 85:
            score -= 10

    # -----------------------------
    # CONDITION LOGIC
    # -----------------------------

    condition = condition.lower()

    good_conditions = {
        "clouds": 10,
        "drizzle": 8,
        "mist": 2,
        "clear": 5
    }

    bad_conditions = {
        "rain": -10,
        "thunderstorm": -35,
        "smoke": -40,
        "haze": -20,
        "dust": -20,
        "fog": -15
    }

    if condition in good_conditions:
        score += good_conditions[condition]

    elif condition in bad_conditions:
        score += bad_conditions[condition]

    # extra punishment:
    # strong sunlight + high heat

    if condition == "clear" and temperature > 34:
        score -= 15

    # -----------------------------
    # WIND LOGIC
    # -----------------------------

    # light breeze feels nice

    if 2 <= wind_speed <= 15:
        score += 5

    elif 16 <= wind_speed <= 30:
        pass

    elif 31 <= wind_speed <= 45:
        score -= 10

    elif wind_speed > 45:
        score -= 20

    return max(0.0, min(100.0, score))


def score_air_quality(aqi: int) -> float:

    mapping = {
        1: 100,
        2: 80,
        3: 55,
        4: 25,
        5: 0
    }

    return mapping.get(aqi, 50)


def score_events(event_count: int) -> float:

    if event_count == 0:
        return 50

    elif event_count == 1:
        return 60

    elif event_count == 2:
        return 70

    elif 3 <= event_count <= 4:
        return 80

    elif 5 <= event_count <= 7:
        return 90

    else:
        return 100


def compute_pulse(
    weather_data: dict,
    air_data: dict,
    events_data: dict
) -> dict:

    weather_score = score_weather(
        weather_data.get("temperature", 25),
        weather_data.get("humidity", 50),
        weather_data.get("condition", "Clear"),
        weather_data.get("wind_speed", 0)
    )

    air_score = score_air_quality(
        air_data.get("aqi", 1)
    )

    events_score = score_events(
        events_data.get("event_count", 0)
    )

    # -----------------------------
    # WEIGHTS
    # -----------------------------

    WEATHER_WEIGHT = _weights["weather"]
    AIR_WEIGHT = _weights["air"]
    EVENTS_WEIGHT = _weights["events"]

    final_score = (
        weather_score * WEATHER_WEIGHT +
        air_score * AIR_WEIGHT +
        events_score * EVENTS_WEIGHT
    )

    # AQI CAP LOGIC

    aqi = air_data.get("aqi", 1)

    if aqi == 5:
        final_score = min(final_score, 45)

    elif aqi == 4:
        final_score = min(final_score, 65)

    return {
        "score": round(final_score, 1),

        "weather_score": round(weather_score, 1),

        "air_score": round(air_score, 1),

        "events_score": round(events_score, 1)
    }