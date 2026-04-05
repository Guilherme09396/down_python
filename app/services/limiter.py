from fastapi import Request, HTTPException
from app.services.cache import r
from app.core.config import RATE_LIMIT

def rate_limit(request: Request):
    ip = request.client.host
    key = f"rate:{ip}"

    count = r.get(key)

    if count and int(count) > RATE_LIMIT:
        raise HTTPException(429, "Too many requests")

    r.incr(key)
    r.expire(key, 60)