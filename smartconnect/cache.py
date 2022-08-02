import json

import redis

from smartconnect import smart_settings

state_key_base = 'er.function.state'

cache = redis.Redis(
    host=smart_settings.REDIS_HOST, port=smart_settings.REDIS_PORT, db=smart_settings.REDIS_DB
)


def save_poll_time(state: str, integration_id: str):
    state_key = f'{state_key_base}.{integration_id}'
    cache.set(state_key, state)


def get_state(integration_id: str):
    state = cache.get(f'{state_key_base}.{integration_id}')

    return json.loads(state) if state else {}

