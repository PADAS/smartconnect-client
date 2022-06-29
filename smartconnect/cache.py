import redis
import smart_settings


cache = redis.Redis(
    host=smart_settings.REDIS_HOST, port=smart_settings.REDIS_PORT, db=smart_settings.REDIS_DB
)
