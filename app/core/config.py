import os

REDIS_URL = os.getenv("REDIS_URL")
print("URL REDIS AQUI", REDIS_URL)

STREAM_TTL = 3600
SEARCH_TTL = 1800
RATE_LIMIT = 100  # req por IP

COOKIES_PATH = os.path.join(os.getcwd(), "cookies.txt")