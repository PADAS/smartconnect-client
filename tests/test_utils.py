import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone
import pytz

import json

from smartconnect import SmartClient, utils

# Testing CA: Sintegrate at connect7.refractions.net:8443/server/connect/home
# CA_UUID = '8f7fbe1b-201a-4ef4-bda8-14f5581e65ce'
CA_LABEL = 'Sintegrate CA [sintegra]'


def test_get_conservation_area():
    smart_client = SmartClient(api='https://connect7.refractions.net:8443/server', username='xxxxx', password='xxxxx', use_language_code='en')

    caslist = smart_client.get_conservation_areas()

    for ca in caslist:
        if ca.label == CA_LABEL:
            ca_uuid = ca.uuid
            break

    print(f'CA UUID: {ca_uuid}')
    predicted_timezone = utils.guess_ca_timezone(ca)
    print(f'{ca.label} -- Predicted_timezone: {predicted_timezone}')

    present = datetime.now(tz=pytz.utc)
    print(f'Now is: {present.astimezone(predicted_timezone)} in {predicted_timezone}')

    dm = smart_client.download_datamodel(ca_uuid=ca_uuid)
    dm.save()

    # smart_client.download_patrolmodel(ca_uuid=ca_uuid)
    # smart_client.download_missionmodel(ca_uuid=ca_uuid)
    
    present = datetime.now(tz=pytz.utc)

    # smart_client.add_incident(ca_uuid=ca_uuid)
    # smart_client.add_patrol_trackpoint(ca_uuid=ca_uuid, device_id='dev-00009', x=-122.4526, y=48.4948, timestamp=present)
    # smart_client.add_mission(ca_uuid=ca_uuid)

