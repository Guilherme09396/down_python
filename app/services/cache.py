import redis
import json
from app.core.config import REDIS_URL

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_cache(key):
    data = r.get(key)
    return json.loads(data) if data else None

def set_cache(key, value, ttl):
    r.setex(key, ttl, json.dumps(value))