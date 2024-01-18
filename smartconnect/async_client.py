import json
import logging
import uuid
from datetime import datetime
from typing import List, Optional, Union

import pytz
import httpx
from pydantic import parse_obj_as

from smartconnect import models, cache, smart_settings, data

logger = logging.getLogger(__name__)

from smartconnect.models import SMARTRequest, SMARTResponse, Patrol, PatrolDataModel, DataModel, ConservationArea, \
    ConfigurableDataModel, SmartConnectApiInfo

DEFAULT_TIMEOUT = (smart_settings.SMART_DEFAULT_CONNECT_TIMEOUT, smart_settings.SMART_DEFAULT_TIMEOUT)


class SMARTClientException(Exception):
    pass


class AsyncSmartClient:
    # TODO: Figure out how to specify timezone.
    SMARTCONNECT_DATFORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, *, api=None, username=None, password=None, use_language_code='en', version="7.5", **kwargs):

        self.api = api.rstrip('/')  # trim trailing slash in case configured into portal with one
        self.username = username
        self.password = password
        self.auth = httpx.BasicAuth(username=self.username, password=self.password)
        self.use_language_code = use_language_code
        self.version = version

        self.logger = logging.getLogger(AsyncSmartClient.__name__)
        self.verify_ssl = smart_settings.SMART_SSL_VERIFY
        # Retries and timeouts settings
        self.max_retries = kwargs.get('max_http_retries', smart_settings.SMART_DEFAULT_CONNECT_RETRIES)
        transport = httpx.AsyncHTTPTransport(retries=self.max_retries)
        connect_timeout = kwargs.get('connect_timeout', smart_settings.SMART_DEFAULT_CONNECT_TIMEOUT)
        data_timeout = kwargs.get('data_timeout', smart_settings.SMART_DEFAULT_TIMEOUT)
        timeout = httpx.Timeout(data_timeout, connect=connect_timeout, pool=connect_timeout)

        # Session
        self._session = httpx.AsyncClient(transport=transport, timeout=timeout, verify=self.verify_ssl)

    async def close(self):
        await self._session.aclose()

    # Support using this client as an async context manager.
    async def __aenter__(self):
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._session.__aexit__()

    async def get_server_api_info(self):
        cas = await self._session.get(
            f'{self.api}/api/info',
            auth=self.auth,
            headers={
                'accept': 'application/json',
            },
        )

        if cas.is_success:
            return SmartConnectApiInfo.parse_obj(cas.json())

        # Just for sanity, log a warning if we get a server error. It's likely it doesn
        if cas.is_server_error:
            logger.warning(f'The SMART Connect server at {self.api} might not support the /api/info request.')

    async def get_conservation_area(self, *, ca_uuid: str = None, force: bool = False):

        cache_key = f"cache:smart-ca:{ca_uuid}:metadata"
        if not force:
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

            for ca in await self.get_conservation_areas():
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

    async def get_conservation_areas(self) -> List[models.ConservationArea]:
        cas = await self._session.get(
            f'{self.api}/api/conservationarea',
            auth=self.auth,
            headers={
                'accept': 'application/json',
            },
        )

        if cas.is_success:
            cas = cas.json()

        return [models.ConservationArea.parse_obj(ca) for ca in cas]

    async def list_configurable_datamodels(self, *, ca_uuid: str):

        assert ca_uuid, "ca_uuid is required"
        '''
        Get metadata about the configurable data models for a given CA.
        :param ca_uuid: The UUID of the CA to get the configurable data models for.
        :return: Smart Connect response that contains the configurable data models.
        '''
        extra_dict = dict(ca_uuid=ca_uuid,
                          url=f'{self.api}/metadata/configurablemodel')

        async with self._session.stream(
                "GET",
                f'{self.api}/api/metadata/configurablemodel',
                auth=self.auth,
                params={"ca_uuid": ca_uuid},
                headers={
                    'accept': 'application/json',
                }
        ) as config_datamodels:
            self.logger.info(
                f'Get configurable data models for CA {ca_uuid} data model took {config_datamodels.elapsed.total_seconds()} seconds',
                extra=dict(**extra_dict, status_code=config_datamodels.status_code))

            if not config_datamodels.is_success:
                self.logger.error(
                    f'Failed to download configurable datamodels for  CA {ca_uuid}. Status_code is: {config_datamodels.status_code}',
                    extra=dict(**extra_dict, status_code=config_datamodels.status_code)
                )
                raise Exception('Failed to download Configurable Data Models')

            cdms = config_datamodels.json()
            return cdms

    async def download_configurable_datamodel(self, *, cm_uuid: str = None):

        extra_dict = dict(cm_uuid=cm_uuid,
                          url=f'{self.api}/api/metadata/configurablemodel/{cm_uuid}')

        async with self._session.stream(
                "GET",
                f'{self.api}/api/metadata/configurablemodel/{cm_uuid}',
                auth=self.auth,
                headers={
                    'accept': 'application/xml',
                },
        ) as config_datamodel:
            self.logger.info(
                f'Download configurable model {cm_uuid} data model took {config_datamodel.elapsed.total_seconds()} seconds',
                extra=dict(**extra_dict, status_code=config_datamodel.status_code)
            )

            if not config_datamodel.is_success:
                self.logger.error(
                    f'Failed to download data model for  configurable model {cm_uuid}. Status_code is: {config_datamodel.status_code}',
                    extra=dict(**extra_dict, status_code=config_datamodel.status_code))
                raise Exception('Failed to download Data Model')

            cdm = ConfigurableDataModel(cm_uuid=cm_uuid, use_language_code=self.use_language_code)
            cdm.load(config_datamodel.text)

            return cdm

    async def get_configurable_data_model(self, *, cm_uuid: str = None, force: bool = False):
        # TODO: version consideration
        # TODO: Implement caching

        ca_uuid = 'na'
        cache_key = f'cache:smart-ca:{ca_uuid}:cdm:{cm_uuid}'

        if not force:
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
        ca_config_datamodel = await self.download_configurable_datamodel(
            cm_uuid=cm_uuid
        )
        cache.cache.set(cache_key, json.dumps(ca_config_datamodel.export_as_dict()))
        return ca_config_datamodel

    async def get_data_model(self, *, ca_uuid: str = None, force: bool = False):

        # CA Data Model is not available for versions below 7. Use a blank data model.
        if self.version.startswith("6"):
            blank_datamodel = DataModel()
            blank_datamodel.load(data.BLANK_DATAMODEL_CONTENT)
            return blank_datamodel

        cache_key = f"cache:smart-ca:{ca_uuid}:datamodel"
        if not force:
            try:
                cached_data = cache.cache.get(cache_key)
                if cached_data:
                    dm = DataModel(use_language_code=self.use_language_code)
                    dm.import_from_dict(json.loads(cached_data))
                    self.logger.debug(
                        f"Using cached SMART Datamodel", extra={"cached_key": cache_key}
                    )
                    return dm

            except Exception as ex:
                logger.exception('Failed on reading data model from cache.', extra={'cache_key': cache_key})

            logger.debug(f"Cache miss for SMART Datamodel", extra={"cached_key": cache_key})

        try:
            ca_datamodel = await self.download_datamodel(
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

    async def download_datamodel(self, *, ca_uuid: str = None):
        extra_dict = dict(
            ca_uuid=ca_uuid,
            url=f'{self.api}/api/metadata/datamodel/{ca_uuid}'
        )
        async with self._session.stream(
                "GET",
                f'{self.api}/api/metadata/datamodel/{ca_uuid}',
                auth=self.auth,
                headers={
                    'accept': 'application/xml',
                },
        ) as response:
            ca_datamodel = await response.aread()
            self.logger.info(f'Download CA {ca_uuid} data model took {response.elapsed.total_seconds()} seconds',
                             extra=dict(**extra_dict, status_code=response.status_code))

            if not response.is_success:
                self.logger.error(
                    f'Failed to download data model for  CA {ca_uuid}. Status_code is: {response.status_code}',
                    extra=dict(**extra_dict, status_code=response.status_code))
                raise Exception('Failed to download Data Model')

            dm = DataModel(use_language_code=self.use_language_code)
            dm.load(ca_datamodel.decode("utf-8"))

            print("Writing data model xml to....")
            with open('gunditest-datamodel.xml', 'w') as fo:
                fo.write(ca_datamodel.decode("utf-8"))

            return dm

    def load_datamodel(self, *, filename=None):
        with open(filename, 'r') as fi:
            contents = fi.read()
            dm = DataModel(use_language_code=self.use_language_code)
            dm.load(contents)
            return dm

    async def download_patrolmodel(self, *, ca_uuid: str = None):
        async with self._session.stream(
                "GET",
                f'{self.api}/api/metadata/patrol/{ca_uuid}',
                auth=self.auth,
                headers={
                    'accept': 'application/json',
                },
        ) as ca_patrolmodel:
            self.logger.info('Downloaded CA Patrol Model. Status code is: %s', ca_patrolmodel.status_code)

            if not ca_patrolmodel.is_success:
                self.logger.error('Failed to download CA Patrol Model. Status_code is: %s', ca_patrolmodel.status_code)
                raise Exception('Failed to download Patrol Model.')

            pm = PatrolDataModel.parse_obj(ca_patrolmodel.json())
            return pm

    async def download_missionmodel(self, *, ca_uuid: str = None):
        async with self._session.stream(
                "GET",
                f'{self.api}/api/metadata/mission/{ca_uuid}',
                auth=self.auth,
                headers={
                    'accept': 'application/json',
                },
        ) as ca_missionmodel:
            self.logger.info('Downloaded CA Mission Model. Status code is: %s', ca_missionmodel.status_code)

            if not ca_missionmodel.is_success:
                self.logger.error('Failed to download CA Mission Model. Status_code is: %s',
                                  ca_missionmodel.status_code)
                raise Exception('Failed to download Mission Model.')

            with open('_missionmodel.json', 'w') as fo:
                fo.write(ca_missionmodel.text)

    def get_patrol_ids(self, *, device_id=None):
        return self.patrol_id_map.setdefault(device_id, {
            'patrol_uuid': str(uuid.uuid4()),
            'patrol_leg_uuid': str(uuid.uuid4())
        })

    async def get_patrol(self, *, patrol_id=None):
        response = await self._session.get(
            f'{self.api}/api/query/custom/patrol',
            auth=self.auth,
            params={"client_patrol_uuid": patrol_id},
        )

        if response.is_success and (json_response := response.json()):
            patrol = parse_obj_as(List[Patrol], json_response)[0]
            return patrol

    async def get_patrol_waypoints(self, *, patrol_id=None):
        response = await self._session.get(
            f'{self.api}/api/query/custom/waypoint/patrol',
            auth=self.auth,
            params={"client_patrol_uuid": patrol_id},
        )

        if response.is_success and (json_response := response.json()):
            smart_response = parse_obj_as(List[SMARTResponse], json_response)
            return [item.properties.waypoint for item in smart_response]

    async def get_incident(self, *, incident_uuid=None):
        url = f'{self.api}/api/query/custom/waypoint/incident'
        response = await self._session.get(
            url,
            auth=self.auth,
            params={"client_incident_uuid": incident_uuid},
        )

        if not response.is_success:
            logger.error("Failed lookup for incident %s", incident_uuid,
                         extra=dict(url=url,
                                    response_content=response.content)
                         )

        response_data = response.json()
        if response_data and isinstance(response_data, list):
            return parse_obj_as(List[SMARTResponse], response_data)

    def generate_patrol_label(self, *, device_id=None, prefix='wildlife', ts=None):
        ts = ts or datetime.now(tz=pytz.utc)
        return '/'.join((prefix, device_id, ts.strftime('%Y/%m')))

    async def post_smart_request(self, *, json: Union[dict, str], ca_uuid: str = None):
        url = f'{self.api}/api/data/{ca_uuid}'
        kwargs = {"auth": self.auth}
        # json payload can be provided as a dict or as a json string
        if isinstance(json, dict):
            kwargs["json"] = json
        elif isinstance(json, str):
            kwargs["data"] = json
            kwargs["headers"] = {"content-type": "application/json"}
        else:
            raise ValueError("json param must be a dict or a json string")
        response = await self._session.post(url, **kwargs)
        if not response.is_success:
            message = f"SMART request failed for {url} with response code {response.status_code}"
            logger.exception(
                message,
                extra=dict(
                    url=url,
                    ca_uuid=ca_uuid,
                    request=json,
                    response=response.content,
                    response_code=response.status_code
                )
            )
            raise SMARTClientException(message)

        logger.info("Posted request to SMART successfully")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "SMART request succeeded",
                extra=dict(
                    url=url,
                    ca_uuid=ca_uuid,
                    request=json,
                    response=response.content,
                    response_code=response.status_code
                ),
            )
        return response.json()

    # Functions for quick testing
    async def add_patrol_trackpoint(self, *, ca_uuid: str = None, patrol_uuid: str = None,
                                    patrol_leg_uuid: str = None, x=None, y=None, timestamp=None):
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

        response = await self._session.post(
            f'{self.api}/api/data/{ca_uuid}',
            json=track_point,
            auth=self.auth,
        )

        if response.is_success:
            print('All good mate!')
        print(response.status_code, response.content)

    async def add_patrol_waypoint(self, *, ca_uuid: str = None, patrol_uuid: str = None,
                                  patrol_leg_uuid: str = None,
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

        response = await self._session.post(
            f'{self.api}/api/data/{ca_uuid}',
            json=way_point,
            auth=self.auth,
        )

        if response.is_success:
            print('All good mate!')
        print(response.status_code, response.content)

    # TODO: Depreciate can just use post_smart_request
    async def add_independent_incident(self, *, incident: models.SMARTRequest, ca_uuid: str = None):

        response = await self._session.post(
            f'{self.api}/api/data/{ca_uuid}',
            json=incident.json(),
            auth=self.auth,
        )

        if response.is_success:
            print('All good mate!')
            print(response.content)
        else:
            logger.error('Failed posting independent incident. %s', response.text)

        logger.debug(response.status_code, response.content)

    async def add_mission(self, *, ca_uuid: str = None):

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
                    "missionUuid": mission_uuid,  # required
                    "survey": '3e6efdfdb3fe4929816ab1f735a80fad',
                    # "team": "communityteam1",
                    "objective": "Tracking wildlife",  # required
                    "comment": "Tracking wildlife",  # required
                    "isArmed": "false",
                    "transportType": "wildlife",  # required
                    "mandate": "animaltracking",  # required
                    # "number": -999,
                    # "test": "test attribute",
                    # "members": ['9b07b0d7155d44de93e8361fede22297'], # Required
                    # "leader": '9b07b0d7155d44de93e8361fede22297',  # required
                }
            }
        }

        response = await self._session.post(
            f'{self.api}/api/data/{ca_uuid}',
            json=track_point,
            auth=self.auth,
        )

        if response.is_success:
            print('All good mate!')
        print(response.status_code, response.content)
