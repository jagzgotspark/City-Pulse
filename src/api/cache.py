import os
import json
import redis
from datetime import datetime, timedelta

CACHE_DURATION = 30 * 60  # 30 minutes in seconds

_redis = None
_fallback = {}

def _get_redis():
    global _redis
    if _redis is None:
        url = os.getenv("REDIS_URL")
        if url:
            try:
                _redis = redis.from_url(url, decode_responses=True)
                _redis.ping()
            except Exception as e:
                print(f"Redis connection failed, using in-memory cache: {e}")
                _redis = None
    return _redis

def get_cached(key: str):
    r = _get_redis()
    if r:
        try:
            value = r.get(key)
            return json.loads(value) if value else None
        except Exception:
            pass
    # fallback
    if key in _fallback:
        cached_time, value = _fallback[key]
        if datetime.utcnow() - cached_time < timedelta(minutes=30):
            return value
    return None

def set_cached(key: str, value):
    r = _get_redis()
    if r:
        try:
            r.setex(key, CACHE_DURATION, json.dumps(value))
            return
        except Exception:
            pass
    # fallback
    _fallback[key] = (datetime.utcnow(), value)