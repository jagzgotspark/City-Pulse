from datetime import datetime, timedelta

_cache = {}
CACHE_DURATION = timedelta(minutes=30)

def get_cached(key: str):
    if key in _cache:
        cached_time, value = _cache[key]
        if datetime.utcnow() - cached_time < CACHE_DURATION:
            return value
    return None

def set_cached(key: str, value):
    _cache[key] = (datetime.utcnow(), value)