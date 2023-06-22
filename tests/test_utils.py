import uuid

from smartconnect.models import ConservationArea
from smartconnect.utils import guess_ca_timezone


def test_guess_ca_timezone():

    val = guess_ca_timezone(ConservationArea(caBoundaryJson='{"type": "Point", "coordinates": [0, 1]}', label='test', status='test', revision='1', uuid=str(uuid.uuid4())))
    # assert val == pytz.timezone('Etc/GMT+1')