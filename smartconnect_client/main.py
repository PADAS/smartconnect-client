import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone
import pytz
from xml.etree import ElementTree
import json
import untangle
import uuid
import local_logging
import logging
import statistics, timezonefinder

from smartconnect import SmartClient

# Testing CA: Sintegrate at connect7.refractions.net:8443/server/connect/home
# CA_UUID = '8f7fbe1b-201a-4ef4-bda8-14f5581e65ce'
CA_LABEL = 'Sintegrate CA [sintegra]'

def get_ca_timezone(ca:dict):

    boundary = json.loads(ca['caBoundaryJson'])

    # with open(f'ca-boundary-{i}.json', 'w') as fo:
    #     json.dump(boundary, fo, indent=2)

    accum = []
    for geometry in boundary['geometries']:
        if geometry['type'] == 'MultiPolygon':
            accum.extend(geometry['coordinates'][0][0])

    avg_longitude = statistics.mean([x[0] for x in accum])
    avg_latitude = statistics.mean([x[1] for x in accum])

    print(f'Average: {avg_longitude}, {avg_latitude}')

    predicted_timezone = timezonefinder.TimezoneFinder().timezone_at(lng=avg_longitude, lat=avg_latitude)        
    # print(f'Predicted timezone: {predicted_timezone}')
    return pytz.timezone(predicted_timezone)


def transform_er_report_to_smart_report(er_report: dict):
    pass

    
if __name__ == '__main__':

    smart_client = SmartClient(api='https://connect7.refractions.net:8443/server', username='sintegrate', password='8adioTwit', use_language_code='en')

    caslist = smart_client.get_conservation_areas()

    # Stash results in a file
    with open('conservationareas.json', 'w') as fo:
        json.dump(caslist, fo, indent=2)

    for cas in caslist:
        if cas.get('label', None) == CA_LABEL:
            ca_uuid = cas.get('uuid')
            break

    print(f'CA UUID: {cas["uuid"]}')
    predicted_timezone = get_ca_timezone(cas)
    print(f'{cas["label"]} -- Predicted_timezone: {predicted_timezone}')

    present = datetime.now(tz=pytz.utc)
    print(f'Now is: {present.astimezone(predicted_timezone)} in {predicted_timezone}')

    # smart_client.download_datamodel(ca_uuid=ca_uuid)
    # smart_client.download_patrolmodel(ca_uuid=ca_uuid)
    # smart_client.download_missionmodel(ca_uuid=ca_uuid)
    
    present = datetime.now(tz=pytz.utc)

    # smart_client.add_incident(ca_uuid=ca_uuid)
    # smart_client.add_patrol_trackpoint(ca_uuid=ca_uuid, device_id='dev-00009', x=-122.4526, y=48.4948, timestamp=present)
    # smart_client.add_mission(ca_uuid=ca_uuid)

