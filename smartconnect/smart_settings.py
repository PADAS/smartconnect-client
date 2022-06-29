from environs import Env

env = Env()
env.read_env()

SMART_SSL_VERIFY = env.bool('SMART_SSL_VERIFY', True)
SMART_DEFAULT_TIMEOUT = env.int('SMART_DEFAULT_TIMEOUT', 60)

# REDIS settings
REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_DB = env.int("REDIS_DB", 3)
