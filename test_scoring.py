from src.scoring.engine import compute_pulse, score_weather, score_air_quality

# Test 1: Perfect conditions
perfect = compute_pulse(
    {"temperature": 25, "humidity": 40, "condition": "Clear", "wind_speed": 2},
    {"aqi": 1},
    {"event_count": 20}
)
print(f"Perfect conditions: {perfect['score']}/100")
assert perfect["score"] > 80, "Perfect conditions should score above 80"

# Test 2: Terrible conditions
terrible = compute_pulse(
    {"temperature": 45, "humidity": 90, "condition": "Thunderstorm", "wind_speed": 15},
    {"aqi": 5},
    {"event_count": 0}
)
print(f"Terrible conditions: {terrible['score']}/100")
assert terrible["score"] < 30, "Terrible conditions should score below 30"

# Test 3: Today's Lucknow (35.99°C, AQI 4)
lucknow_today = compute_pulse(
    {"temperature": 35.99, "humidity": 45, "condition": "Clear", "wind_speed": 3.5},
    {"aqi": 4},
    {"event_count": 5}
)
print(f"Lucknow today: {lucknow_today['score']}/100")

# Test 4: Score never goes below 0 or above 100
assert 0 <= perfect["score"] <= 100
assert 0 <= terrible["score"] <= 100
assert 0 <= lucknow_today["score"] <= 100

# Test 5: Missing data handled gracefully
missing = compute_pulse({}, {}, {})
print(f"Missing data: {missing['score']}/100")
assert 0 <= missing["score"] <= 100

print("\nAll tests passed.")