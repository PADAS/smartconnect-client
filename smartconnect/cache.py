import redis
import uuid
import json

cache = redis.Redis(host='localhost', port='30091', db=4)


def ensure_patrol(patrol_label):

    patrol_ids = cache.get(patrol_label)

    if patrol_ids:
        return json.loads(patrol_ids)

    patrol_ids = {
        'patrol_uuid': str(uuid.uuid4()),
        'patrol_leg_uuid': str(uuid.uuid4())
        }

    cache.setex(patrol_label, 86400*365, json.dumps(patrol_ids))

    return patrol_ids