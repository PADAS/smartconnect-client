import json
import logging
import uuid
from datetime import datetime
from typing import List, Optional

import pytz
import requests
from pydantic import parse_obj_as
from pydantic.main import BaseModel
from requests.auth import HTTPBasicAuth

from smartconnect import models, cache, smart_settings

logger = logging.getLogger(__name__)

from smartconnect.models import SMARTRequest, SMARTResponse, Patrol, PatrolDataModel, DataModel

# Manually bump this.
__version__ = '1.0.3'

DEFAULT_TIMEOUT = (3.1, 60)


class SMARTClientException(Exception):
    pass


class SmartClient:

    # TODO: Figure out how to specify timezone.
    SMARTCONNECT_DATFORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, *, api=None, username=None, password=None, use_language_code='en'):
        self.api = api.rstrip('/')  # trim trailing slash in case configured into portal with one
        self.username = username
        self.password = password
        self.auth=HTTPBasicAuth(self.username, self.password)
        self.use_language_code=use_language_code

        self.logger = logging.getLogger(SmartClient.__name__)
        self.verify_ssl = smart_settings.SMART_SSL_VERIFY

    def get_conservation_areas(self) -> List[models.ConservationArea]:
        cas = requests.get(f'{self.api}/api/conservationarea',
                            auth=self.auth,
                            headers={
                                'accept': 'application/json',
                            },
                            verify=self.verify_ssl,
                            timeout=DEFAULT_TIMEOUT
                            )

        if cas.ok:
            cas = cas.json()

        return [models.ConservationArea.parse_obj(ca) for ca in cas]

    def download_datamodel(self, *, ca_uuid: str = None):

        ca_datamodel = requests.get(f'{self.api}/api/metadata/datamodel/{ca_uuid}',
            auth=self.auth,
            headers={
                'accept': 'application/xml',
            },
            stream=True,
            verify=self.verify_ssl,
            timeout=DEFAULT_TIMEOUT)
        ca_datamodel.raw.decode_content = True

        self.logger.debug(f'Download CA Data model took {ca_datamodel.elapsed.total_seconds()} seconds')

        self.logger.info('Downloaded CA Datamodel. Status code is: %s', ca_datamodel.status_code)

        if not ca_datamodel.ok:
            self.logger.error('Failed to download CA Datamodel. Status_code is: %s', ca_datamodel.status_code)
            raise Exception('Failed to download Data Model.')


        dm = DataModel()
        dm.load(ca_datamodel.text)
        return dm

    def download_patrolmodel(self, *, ca_uuid: str = None):

        ca_patrolmodel = requests.get(f'{self.api}/api/metadata/patrol/{ca_uuid}',
            auth=self.auth,
            headers={
                'accept': 'application/json',
            },
            stream=True,
            verify=self.verify_ssl,
            timeout=DEFAULT_TIMEOUT)
        ca_patrolmodel.raw.decode_content = True

        self.logger.info('Downloaded CA Patrol Model. Status code is: %s', ca_patrolmodel.status_code)

        if not ca_patrolmodel.ok:
            self.logger.error('Failed to download CA Patrol Model. Status_code is: %s', ca_patrolmodel.status_code)
            raise Exception('Failed to download Patrol Model.')

        pm = PatrolDataModel.parse_obj(json.loads(ca_patrolmodel.text))
        return pm

    def download_missionmodel(self, *, ca_uuid: str = None):

        ca_missionmodel = requests.get(f'{self.api}/api/metadata/mission/{ca_uuid}',
            auth=self.auth,
            headers={
                'accept': 'application/json',
            },
            stream=True,
            verify=self.verify_ssl,
            timeout=DEFAULT_TIMEOUT)
        ca_missionmodel.raw.decode_content = True

        self.logger.info('Downloaded CA Mission Model. Status code is: %s', ca_missionmodel.status_code)

        if not ca_missionmodel.ok:
            self.logger.error('Failed to download CA Mission Model. Status_code is: %s', ca_missionmodel.status_code)
            raise Exception('Failed to download Mission Model.')


        with open('_missionmodel.json', 'w') as fo:
            fo.write(ca_missionmodel.text)

    def get_patrol_ids(self, *, device_id=None):

        return self.patrol_id_map.setdefault(device_id, {
            'patrol_uuid': str(uuid.uuid4()),
            'patrol_leg_uuid': str(uuid.uuid4())
        })

    def get_patrol(self, *, patrol_id=None):
        patrol = None
        response = requests.get(f'{self.api}/api/query/custom/patrol',
                                 auth=self.auth,
                                 params= {"client_patrol_uuid": patrol_id},
                                 verify=self.verify_ssl,
                                 timeout=DEFAULT_TIMEOUT)
        if response.ok and len(response.json()) > 0:
            patrol = parse_obj_as(List[Patrol],response.json())[0]
        return patrol

    def get_patrol_waypoints(self, *, patrol_id=None):
        waypoints = None
        response = requests.get(f'{self.api}/api/query/custom/waypoint/patrol',
                                 auth=self.auth,
                                 params= {"client_patrol_uuid": patrol_id},
                                 verify=self.verify_ssl,
                                 timeout=DEFAULT_TIMEOUT)

        if response.ok and len(response.json()) > 0:
            smart_response = parse_obj_as(List[SMARTResponse],response.json())
            waypoints = [item.properties.waypoint for item in smart_response]
        return waypoints

    def get_incident(self, *, incident_uuid=None):
        smart_response = None
        response = requests.get(f'{self.api}/api/query/custom/waypoint/incident',
                                auth=self.auth,
                                params={"client_incident_uuid": incident_uuid},
                                verify=self.verify_ssl,
                                timeout=DEFAULT_TIMEOUT)

        if response.ok and len(response.json()) > 0:
            smart_response = parse_obj_as(List[SMARTResponse], response.json())
        return smart_response

    def generate_patrol_label(self, *, device_id=None, prefix='wildlife', ts=None):

        ts = ts or datetime.now(tz=pytz.utc)

        return '/'.join( (prefix, device_id, ts.strftime('%Y/%m')) )

    def post_smart_request(self, *, json: str, ca_uuid: str = None):
        response = requests.post(f'{self.api}/api/data/{ca_uuid}',
                                 headers={'content-type': 'application/json'},
                                 data=json,
                                 auth=self.auth,
                                 timeout=DEFAULT_TIMEOUT,
                                 verify=self.verify_ssl)
        if response.ok:
            logger.info("posted request to SMART successfully")
        else:
            logger.error("SMART request Failed", extra=dict(ca_uuid=ca_uuid,
                                                            request=json,
                                                            response=response.content))
            raise SMARTClientException

    # Functions for quick testing
    def add_patrol_trackpoint(self, *, ca_uuid: str = None, patrol_uuid: str = None, patrol_leg_uuid: str = None, x=None, y=None, timestamp=None):
        track_point = {
            "type": "Feature",
            "geometry": {
                "coordinates": [x, y],
                "type": "Point"
            },
            "properties": {
                "dateTime": timestamp.strftime(self.SMARTCONNECT_DATFORMAT),

                "smartDataType": "patrol",
                "smartFeatureType": "trackpoint/new",
                "smartAttributes": {
                    "patrolUuid": patrol_uuid,  # required
                    "patrolLegUuid": patrol_leg_uuid,  # required
                }
            }
        }

        response = requests.post(f'{self.api}/api/data/{ca_uuid}',
                                 json=track_point,
                                 auth=self.auth,
                                 verify=self.verify_ssl)

        if response.ok:
            print('All good mate!')
        print(response.status_code, response.content)

    def add_patrol_waypoint(self, *, ca_uuid: str = None, patrol_uuid: str = None, patrol_leg_uuid: str = None,
                              x=None, y=None, timestamp=None):
        way_point = {
            "type": "Feature",
            "geometry": {
                "coordinates": [x, y],
                "type": "Point"
            },
            "properties": {
                "dateTime": timestamp.strftime(self.SMARTCONNECT_DATFORMAT),

                "smartDataType": "patrol",
                "smartFeatureType": "waypoint/new",
                "smartAttributes": {
                    "patrolUuid": patrol_uuid,  # required
                    "patrolLegUuid": patrol_leg_uuid,  # required
                }
            }
        }

        response = requests.post(f'{self.api}/api/data/{ca_uuid}',
                                 json=way_point,
                                 auth=self.auth,
                                 verify=self.verify_ssl)

        if response.ok:
            print('All good mate!')
        print(response.status_code, response.content)
    # TODO: Depreciate can just use post_smart_request
    def add_independent_incident(self, *, incident: models.SMARTRequest, ca_uuid: str = None):

        response = requests.post(f'{self.api}/api/data/{ca_uuid}', headers={'content-type': 'application/json'},
            data=incident.json(), auth=self.auth, timeout=(3.1, 10), verify=self.verify_ssl)

        if response.ok:
            print('All good mate!')
            print(response.content)
        else:
            logger.error('Failed posting independent incident. %s', response.text)

        logger.debug(response.status_code, response.content)

    def add_mission(self, *, ca_uuid: str = None):

        present = datetime.now(tz=pytz.utc)

        mission_uuid = str(uuid.uuid4())

        print(f'Using Mission id: {mission_uuid}')
        track_point = {
            "type": "Feature",
            "geometry": {
            "coordinates": [11.41, -9.2],
            "type": "Point"
            },
            "properties": {
            "dateTime": present.strftime(self.SMARTCONNECT_DATFORMAT),

            "smartDataType": "mission",
            "smartFeatureType": "start",
            "smartAttributes": {
                'missionId': 'wildilfe/2021/07/mission-00004',
                "missionUuid": mission_uuid, # required
                "survey": '3e6efdfdb3fe4929816ab1f735a80fad',
                # "team": "communityteam1",
                "objective": "Tracking wildlife",   #required
                "comment": "Tracking wildlife",     #required
                "isArmed": "false",
                "transportType": "wildlife",        #required
                "mandate": "animaltracking",        #required
                # "number": -999,
                # "test": "test attribute",
                # "members": ['9b07b0d7155d44de93e8361fede22297'], # Required
                # "leader": '9b07b0d7155d44de93e8361fede22297',  # required
            }
            }
        }



        response = requests.post(f'{self.api}/api/data/{ca_uuid}',
                                 json=track_point,
                                 auth=self.auth,
                                 verify=self.verify_ssl)

        if response.ok:
            print('All good mate!')
        print(response.status_code, response.content)




