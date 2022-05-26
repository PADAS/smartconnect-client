from environs import Env

env = Env()
env.read_env()

SMART_SSL_VERIFY = env.bool('SMART_SSL_VERIFY', True)
SMART_DEFAULT_TIMEOUT = env.int('SMART_DEFAULT_TIMEOUT', 60)
