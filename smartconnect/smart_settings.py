from environs import Env

env = Env()
env.read_env()

SMART_SSL_VERIFY = env.bool('SMART_SSL_VERIFY', True)
SMART_DEFAULT_TIMEOUT = env.int('SMART_DEFAULT_TIMEOUT', 60)
SMART_DEFAULT_CONNECT_TIMEOUT = env.int('SMART_DEFAULT_CONNECT_TIMEOUT', 3.1)
SMART_DEFAULT_CONNECT_RETRIES = env.int('SMART_DEFAULT_CONNECT_RETRIES', 5)

# How long cached SMART metadata (CA, data model, configurable models) lives in Redis.
# The portal re-primes the cache when an integration is saved or maintained; this is the backstop.
SMART_CACHE_TTL_SECONDS = env.int('SMART_CACHE_TTL_SECONDS', 60 * 60 * 24 * 30)

# REDIS settings
REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_DB = env.int("REDIS_DB", 3)
