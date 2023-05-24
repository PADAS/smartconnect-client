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

from smartconnect import models, cache, smart_settings, data

logger = logging.getLogger(__name__)

from smartconnect.models import SMARTRequest, SMARTResponse, Patrol, PatrolDataModel, DataModel, ConservationArea, \
    ConfigurableDataModel, SmartConnectApiInfo

# Manually bump this.
__version__ = '1.0.3'

DEFAULT_TIMEOUT = (3.1, smart_settings.SMART_DEFAULT_TIMEOUT)


class SMARTClientException(Exception):
    pass

class SmartClient:

    # TODO: Figure out how to specify timezone.
    SMARTCONNECT_DATFORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, *args, api=None, username=None, password=None, use_language_code='en', version="7.5"):

        assert not args, "This function does not accept positional arguments"

        self.api = api.rstrip('/')  # trim trailing slash in case configured into portal with one
        self.username = username
        self.password = password
        self.auth=HTTPBasicAuth(self.username, self.password)
        self.use_language_code=use_language_code
        self.version=version

        self.logger = logging.getLogger(SmartClient.__name__)
        self.verify_ssl = smart_settings.SMART_SSL_VERIFY

    def get_server_api_info(self):
        cas = requests.get(f'{self.api}/api/info',
                           auth=self.auth,
                           headers={
                               'accept': 'application/json',
                           },
                           verify=self.verify_ssl,
                           timeout=DEFAULT_TIMEOUT
                           )

        if cas.ok:
            return SmartConnectApiInfo.parse_obj(cas.json())

    def get_conservation_area(self, *args, ca_uuid: str = None, use_cache: bool = True):

        assert not args, "This function does not accept positional arguments"

        cache_key = f"cache:smart-ca:{ca_uuid}:metadata"
        if use_cache:
            self.logger.info(f"Looking up CA cached at {cache_key}.")
            try:
                cached_data = cache.cache.get(cache_key)
                if cached_data:
                    self.logger.info(f"Found CA cached at {cache_key}.")
                    conservation_area = ConservationArea.parse_raw(cached_data)
                    return conservation_area

                self.logger.info(f"Cache miss for {cache_key}")
            except:
                self.logger.info(f"Cache miss/error for {cache_key}")
                pass

        try:
            self.logger.info(
                "Querying Smart Connect for CAs at endpoint: %s, username: %s",
                self.api,
                self.username,
            )

            for ca in self.get_conservation_areas():
                if ca.uuid == uuid.UUID(ca_uuid):
                    conservation_area = ca
                    break
            else:
                logger.error(
                    f"Can't find a Conservation Area with UUID: {ca_uuid}"
                )
                conservation_area = None

            if conservation_area:
                self.logger.info(f"Caching CA metadata at {cache_key}")
                cache.cache.set(
                    name=cache_key,
                    value=json.dumps(dict(conservation_area), default=str),
                )

            return conservation_area

        except Exception as ex:
            self.logger.exception(
                f"Failed to get Conservation Areas", extra=dict(ca_uuid=ca_uuid)
            )
            raise SMARTClientException(f"Failed to get SMART Conservation Areas") from ex

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

    def list_configurable_datamodels(self, *args, ca_uuid: str):

        assert not args, "Only keyword arguments"
        assert ca_uuid, "ca_uuid is required"
        '''
        Get metadata about the configurable data models for a given CA.
        :param ca_uuid: The UUID of the CA to get the configurable data models for.
        :return: Smart Connect response that contains the configurable data models.
        '''
        extra_dict = dict(ca_uuid=ca_uuid,
                          url=f'{self.api}/metadata/configurablemodel')

        config_datamodels = requests.get(f'{self.api}/api/metadata/configurablemodel',
                                        auth=self.auth,
                                        params={"ca_uuid": ca_uuid},
                                        headers={
                                            'accept': 'application/json',
                                        },
                                        stream=True,
                                        verify=self.verify_ssl,
                                        timeout=DEFAULT_TIMEOUT)

        config_datamodels.raw.decode_content = True

        self.logger.info(f'Get configurable data models for CA {ca_uuid} data model took {config_datamodels.elapsed.total_seconds()} seconds',
                         extra=dict(**extra_dict,
                                    status_code=config_datamodels.status_code))

        if not config_datamodels.ok:
            self.logger.error(
                f'Failed to download configurable datamodels for  CA {ca_uuid}. Status_code is: {config_datamodels.status_code}',
                extra=dict(**extra_dict,
                           status_code=config_datamodels.status_code))
            raise Exception('Failed to download Configurable Data Models')

        cdms = config_datamodels.json()
        return cdms

    def download_configurable_datamodel(self, *args, cm_uuid: str = None):

        assert not args, "Only keyword arguments are allowed"

        extra_dict = dict(cm_uuid=cm_uuid,
                          url=f'{self.api}/api/metadata/configurablemodel/{cm_uuid}')

        config_datamodel = requests.get(f'{self.api}/api/metadata/configurablemodel/{cm_uuid}',
                                    auth=self.auth,
                                    headers={
                                        'accept': 'application/xml',
                                    },
                                    stream=True,
                                    verify=self.verify_ssl,
                                    timeout=DEFAULT_TIMEOUT)
        config_datamodel.raw.decode_content = True

        self.logger.info(f'Download configurable model {cm_uuid} data model took {config_datamodel.elapsed.total_seconds()} seconds',
                         extra=dict(**extra_dict,
                                    status_code=config_datamodel.status_code))

        if not config_datamodel.ok:
            self.logger.error(
                f'Failed to download data model for  configurable model {cm_uuid}. Status_code is: {config_datamodel.status_code}',
                extra=dict(**extra_dict,
                           status_code=config_datamodel.status_code))
            raise Exception('Failed to download Data Model')

        cdm = ConfigurableDataModel(cm_uuid=cm_uuid)
        cdm.load(config_datamodel.text)
        
        return cdm

    def get_configurable_data_model(self, *args, cm_uuid: str = None, use_cache: bool = True):
        # TODO: version consideration
        # TODO: Implement caching

        assert not args, "Only keyword arguments are allowed"

        ca_uuid = 'na'
        cache_key = f'cache:smart-ca:{ca_uuid}:cdm:{cm_uuid}'

        if use_cache:
            try:
                cached_data = cache.cache.get(cache_key)
                if cached_data:

                    cm = ConfigurableDataModel(use_language_code=self.use_language_code)
                    cm.import_from_dict(json.loads(cached_data))

                    self.logger.debug(
                        f"Using cached SMART Configurable Data Model", extra={"cached_key": cache_key}
                    )
                    return cm

            except Exception as ex:
                logger.exception('Failed on reading configurable model from cache.', extra={'cache_key': cache_key})

        # Re-download and cache.
        ca_config_datamodel = self.download_configurable_datamodel(
            cm_uuid=cm_uuid
        )
        cache.cache.set(cache_key, json.dumps(ca_config_datamodel.export_as_dict()))
        return ca_config_datamodel

    def get_data_model(self, *args, ca_uuid: str = None, use_cache: bool = True):

        assert not args, "get_data_model() takes no positional arguments."

        # CA Data Model is not available for versions below 7. Use a blank data model.
        if self.version.startswith("6"):
            blank_datamodel = DataModel()
            blank_datamodel.load(data.BLANK_DATAMODEL_CONTENT)
            return blank_datamodel

        cache_key = f"cache:smart-ca:{ca_uuid}:datamodel"
        if use_cache:
            try:
                cached_data = cache.cache.get(cache_key)
                if cached_data:
                    dm = DataModel()
                    dm.import_from_dict(json.loads(cached_data))
                    self.logger.debug(
                        f"Using cached SMART Datamodel", extra={"cached_key": cache_key}
                    )
                    return dm

            except Exception as ex:
                logger.exception('Failed on reading data model from cache.', extra={'cache_key': cache_key})

            logger.debug(f"Cache miss for SMART Datamodel", extra={"cached_key": cache_key})

        try:
            ca_datamodel = self.download_datamodel(
                ca_uuid=ca_uuid
            )
        except Exception as e:
            logger.exception(e)
            raise SMARTClientException(f"Failed downloading SMART Datamodel for CA {ca_uuid}") from e

        if ca_datamodel:
            cache.cache.set(
                name=cache_key,
                value=json.dumps(ca_datamodel.export_as_dict()),
            )

        return ca_datamodel

    def download_datamodel(self, *args, ca_uuid: str = None):

        assert not args, "Only keyword arguments are allowed"

        extra_dict = dict(ca_uuid=ca_uuid,
                          url=f'{self.api}/api/metadata/datamodel/{ca_uuid}')

        ca_datamodel = requests.get(f'{self.api}/api/metadata/datamodel/{ca_uuid}',
                                    auth=self.auth,
                                    headers={
                                        'accept': 'application/xml',
                                    },
                                    stream=True,
                                    verify=self.verify_ssl,
                                    timeout=DEFAULT_TIMEOUT)
        ca_datamodel.raw.decode_content = True

        self.logger.info(f'Download CA {ca_uuid} data model took {ca_datamodel.elapsed.total_seconds()} seconds',
                         extra=dict(**extra_dict,
                                    status_code=ca_datamodel.status_code))

        if not ca_datamodel.ok:
            self.logger.error(
                f'Failed to download data model for  CA {ca_uuid}. Status_code is: {ca_datamodel.status_code}',
                extra=dict(**extra_dict,
                           status_code=ca_datamodel.status_code))
            raise Exception('Failed to download Data Model')

        dm = DataModel()
        dm.load(ca_datamodel.text)
        return dm

    def load_datamodel(self, *args, filename=None):

        assert not args, "Only keyword arguments are allowed"

        with open(filename, 'r') as fi:
            contents = fi.read()

            dm = DataModel(use_language_code=self.use_language_code)
            dm.load(contents)
            return dm
        
    def download_patrolmodel(self, *args, ca_uuid: str = None):

        assert not args, "Only keyword arguments are allowed"

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

        pm = PatrolDataModel.parse_obj(ca_patrolmodel.json())
        return pm

    def download_missionmodel(self, *args, ca_uuid: str = None):

        assert not args, "Only keyword arguments are allowed"

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

    def get_patrol_ids(self, *args, device_id=None):

        assert not args, "get_patrol_ids() takes no positional arguments."

        return self.patrol_id_map.setdefault(device_id, {
            'patrol_uuid': str(uuid.uuid4()),
            'patrol_leg_uuid': str(uuid.uuid4())
        })

    def get_patrol(self, *args, patrol_id=None):
        assert not args, "get_patrol() takes no positional arguments."
        patrol = None
        response = requests.get(f'{self.api}/api/query/custom/patrol',
                                 auth=self.auth,
                                 params= {"client_patrol_uuid": patrol_id},
                                 verify=self.verify_ssl,
                                 timeout=DEFAULT_TIMEOUT)

        if response.ok and len(response.json()) > 0:
            patrol = parse_obj_as(List[Patrol],response.json())[0]
        return patrol

    def get_patrol_waypoints(self, *args, patrol_id=None):
        assert not args, "get_patrol_waypoints() takes no positional arguments."
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

    def get_incident(self, *args, incident_uuid=None):
        assert not args, "get_incident() takes no positional arguments."
        smart_response = None
        url = f'{self.api}/api/query/custom/waypoint/incident'
        response = requests.get(url,
                                auth=self.auth,
                                params={"client_incident_uuid": incident_uuid},
                                verify=self.verify_ssl,
                                timeout=DEFAULT_TIMEOUT)

        if response.ok and len(response.json()) > 0:
            smart_response = parse_obj_as(List[SMARTResponse], response.json())
        else:
            logger.error("Bad response from SMART Connect", extra=dict(url=url,
                                                                       response_content=response.content))
        return smart_response

    def generate_patrol_label(self, *args, device_id=None, prefix='wildlife', ts=None):
        assert not args, "generate_patrol_label() takes no positional arguments."
        ts = ts or datetime.now(tz=pytz.utc)

        return '/'.join( (prefix, device_id, ts.strftime('%Y/%m')) )

    def post_smart_request(self, *args, json: str, ca_uuid: str = None):
        assert not args, "post_smart_request() takes no positional arguments."

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
            raise SMARTClientException("SMART request Failed")

    # Functions for quick testing
    def add_patrol_trackpoint(self, *args, ca_uuid: str = None, patrol_uuid: str = None, patrol_leg_uuid: str = None, x=None, y=None, timestamp=None):
        assert not args, "add_patrol_trackpoint() takes no positional arguments."
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

    def add_patrol_waypoint(self, *args, ca_uuid: str = None, patrol_uuid: str = None, patrol_leg_uuid: str = None,
                              x=None, y=None, timestamp=None):
        assert not args, "add_patrol_waypoint() takes no positional arguments."
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
    def add_independent_incident(self, *args, incident: models.SMARTRequest, ca_uuid: str = None):
        assert not args, "add_independent_incident() takes no positional arguments."

        response = requests.post(f'{self.api}/api/data/{ca_uuid}', headers={'content-type': 'application/json'},
            data=incident.json(), auth=self.auth, timeout=(3.1, 10), verify=self.verify_ssl)

        if response.ok:
            print('All good mate!')
            print(response.content)
        else:
            logger.error('Failed posting independent incident. %s', response.text)

        logger.debug(response.status_code, response.content)

    def add_mission(self, *args, ca_uuid: str = None):
        assert not args, "add_mission() takes no positional arguments."
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




