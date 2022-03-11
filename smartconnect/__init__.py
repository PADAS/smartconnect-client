import requests
from pydantic.main import BaseModel
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import pytz
import untangle
import uuid
import json
from smartconnect import models, cache, smart_settings
from typing import List, Optional

import logging

logger = logging.getLogger(__name__)

# Manually bump this.
__version__ = '1.0.0'

class SmartClient:

    # TODO: Figure out how to specify timezone.
    SMARTCONNECT_DATFORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, *, api=None, username=None, password=None, use_language_code='en'):
        self.api = api
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
                            verify=self.verify_ssl
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
            verify=self.verify_ssl)
        ca_datamodel.raw.decode_content = True    

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
            verify=self.verify_ssl)
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
            verify=self.verify_ssl)
        ca_missionmodel.raw.decode_content = True    

        self.logger.info('Downloaded CA Mission Model. Status code is: %s', ca_missionmodel.status_code)

        if not ca_missionmodel.ok:
            self.logger.error('Failed to download CA Mission Model. Status_code is: %s', ca_missionmodel.status_code)
            raise Exception('Failed to download Mission Model.')


        with open('_missionmodel.json', 'w') as fo:
            fo.write(ca_missionmodel.text)


    def add_independent_incident(self, *, incident: models.IndependentIncident, ca_uuid: str = None):
        
        response = requests.post(f'{self.api}/api/data/{ca_uuid}', headers={'content-type': 'application/json'}, 
            data=incident.json(), auth=self.auth, timeout=(3.1, 10), verify=self.verify_ssl)

        if response.ok:
            print('All good mate!')
            print(response.content)
        else:
            logger.error('Failed posting independent incident. %s', response.text)

        logger.debug(response.status_code, response.content)

    # def add_incident(self, *, ca_uuid: str = None):
        
    #     present = datetime.now(tz=pytz.utc)


    #     incident_data = {
    #         'type': 'Feature',
    #         'geometry': {
    #             'coordinates': [-122.54, 48.475],
    #             'type': 'Point',
    #         },

    #         'properties': {
    #             'dateTime': present.strftime(self.SMARTCONNECT_DATFORMAT),
    #             'smartDataType': 'incident',
    #             'smartFeatureType': 'observation',
    #             'smartAttributes': {
    #                 'observationGroups': [
    #                     {
    #                         'observations': [
    #                             {
    #                                 'category': 'animals.carcass',
    #                                 'attributes': {
    #                                     'causeofdeath': 'natural.depression',
    #                                     #'species': 'chordata_rl.reptilia_rl.squamata_rl.amphisbaenidae_rl.blanus_rl.blanuscinereus_rl61469',
    #                                     'species': 'chordata_rl.mammalia_rl.proboscidea_rl.elephantidae_rl.loxodonta_rl', #.loxodontaafricana_rl12392'
    #                                 },
                                    
    #                             }
    #                         ]
    #                     }                    
    #                 ]

    #             }
    #         }
    #     }

    #     print(json.dumps(incident_data, indent=2))
    #     response = requests.post(f'{self.api}/api/data/{ca_uuid}', json=incident_data, auth=self.auth)

    #     if response.ok:
    #         print('All good mate!')
    #     print(response.status_code, response.content)

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

    def get_patrol_ids(self, *, device_id=None):

        return self.patrol_id_map.setdefault(device_id, {
            'patrol_uuid': str(uuid.uuid4()),
            'patrol_leg_uuid': str(uuid.uuid4())
        })
        
    def generate_patrol_label(self, *, device_id=None, prefix='wildlife', ts=None):

        ts = ts or datetime.now(tz=pytz.utc)

        return '/'.join( (prefix, device_id, ts.strftime('%Y/%m')) )


    def add_patrol_trackpoint(self, *, ca_uuid: str = None, device_id: str = None, x=None, y=None, timestamp=None):

        # present = datetime.now(tz=pytz.utc) - timedelta(minutes=15)

        patrol_label = self.generate_patrol_label(device_id=device_id, prefix='wildlife', ts=timestamp)
        patrol_ids = cache.ensure_patrol(patrol_label)

        patrol_start = {
            "type": "Feature",
            "geometry": {
            "coordinates": [x, y],
            "type": "Point"
            },
            "properties": {
            "dateTime": timestamp.strftime(self.SMARTCONNECT_DATFORMAT),
            
            "smartDataType": "patrol",
            "smartFeatureType": "start",
            "smartAttributes": {
                'patrolId': patrol_label,
                "patrolUuid": patrol_ids['patrol_uuid'], # required #generated-by-client
                "patrolLegUuid": patrol_ids['patrol_leg_uuid'],  # required #generated-by-client
                "objective": "Tracking wildlife",   #required #free-text
                "comment": "Tracking wildlife",     #required #free-text
                "isArmed": "false",
                "transportType": "wildlife",        #required #must-exist-in-smart
                "mandate": "animaltracking",        #required
                "members": ['9b07b0d7155d44de93e8361fede22297'], # Required #must-exist-in-smart
                "leader": '9b07b0d7155d44de93e8361fede22297',  # required #must-exist-in-smart
            }
            }
        }

        track_point = {
            "type": "Feature",
            "geometry": {
            "coordinates": [x, y],
            "type": "Point"
            },
            "properties": {
                "dateTime": timestamp.strftime(self.SMARTCONNECT_DATFORMAT),
                
                "smartDataType": "patrol",
                "smartFeatureType": "trackpoint",
                "smartAttributes": {
                    'patrolId': patrol_label,
                    "patrolUuid": patrol_ids['patrol_uuid'], # required
                    "patrolLegUuid": patrol_ids['patrol_leg_uuid'],  # required
                }
            }
        }

        for _ in range(2):
            '''
            I'll try once, possibly failing on 'no patrol present'. If that happens we'll create
            a patrol and-repost the track-point.
            
            # TODO: if we decide we need to 'start' a patrol, can we forego the track-point?
            '''
            response = requests.post(f'{self.api}/api/data/{ca_uuid}',
                                     json=track_point,
                                     auth=self.auth,
                                     verify=self.verify_ssl)

            if response.ok:
                logger.info('Posted track point for Patrol Label: %s. Context is %s', patrol_label, response.text)
                break
            if response.status_code == 400: # < Likely there isn't a patrol started.
                
                data = response.json()
                
                if patrol_ids['patrol_leg_uuid'] in data.get('error', ''):
                    patrol_start_response = requests.post(f'{self.api}/api/data/{ca_uuid}',
                                                          json=patrol_start,
                                                          auth=self.auth,
                                                          verify=self.verify_ssl)

                    if patrol_start_response.ok:
                        logger.info('Started Patrol for label: %s', patrol_label)
                    else:                        
                        logger.error('Failed to start a patrol for label: %s', patrol_label)
                        break
                    

class DataModel:

    def __init__(self, use_language_code='en'):
        self.use_language_code = use_language_code

    def load(self, datamodel_text):
        self.datamodel = untangle.parse(datamodel_text)

        self._categories = list(self.generate_category_paths(self.datamodel.DataModel.categories))
        self._attributes = list(self.generate_attributes(self.datamodel.DataModel.attributes))

    def save(self, filename='_si-datamodel.json'):
        with open('_si-datamodel.json', 'w') as fo:
            json.dump({
                'categories': self._categories,
                'attributes': self._attributes,
            }, fo, indent=2)

    def export_as_dict(self):
        return {
                'categories': self._categories,
                'attributes': self._attributes,
            }

    def import_from_dict(self, data:dict):
        self._categories = data.get('categories')
        self._attributes = data.get('attributes')

    def get_category(self, *, path: str = None) -> dict:
        for cat in self._categories:
            if cat['path'] == path:
                return cat

    def get_attribute(self, *, key:str = None) -> dict:
        for att in self._attributes:
            if att['key'] == key:
                return att

    def generate_category_attributes(self, root):
        if hasattr(root, 'attribute'):
            for attribute in root.attribute:
                yield {
                    'key': attribute['attributekey'],
                    'isactive': attribute['isactive'] == 'true'
                }

    def get_list_options(self, attribute):
        if hasattr(attribute, 'values'):
            yield from [{
                'key': value['key'],
                'display': self.resolve_display(value.names, language_code=self.use_language_code)
            } for value in attribute.values]

    def get_tree_options(self, attribute):
        if hasattr(attribute, 'tree'):

            for tree_value in attribute.tree:
                val = {
                    'key': tree_value['key'],
                    'display': self.resolve_display(tree_value.names, language_code=self.use_language_code)
                }
                yield val
                yield from self.generate_tree_children(tree_value, prefix=val['key'])

    def generate_tree_children(self, branch, prefix=''):
        if hasattr(branch, 'children'):
            for elem in branch.children:
                
                if elem._name == 'children': 
                    child = elem
                
                    this_key = '.'.join([prefix, child['key']])
                    val = {
                        'key': this_key,
                        'display': self.resolve_display(child.names, language_code=self.use_language_code),
                    }
                    yield val
                    yield from self.generate_tree_children(child, prefix=this_key)


    def generate_category_paths(self, root, prefix=None):
        '''

        '''
        if hasattr(root, 'category'):
            for subcat in root.category:
                if prefix:
                    yield {
                        'path': f'{prefix}.{subcat["key"]}',
                        'ismultiple': subcat['ismultiple'],
                        'attributes': list(self.generate_category_attributes(subcat)),
                        'display': self.resolve_display(subcat.names, language_code=self.use_language_code)
                    }
                    new_prefix = f'{prefix}.{subcat["key"]}'
                else:
                    yield {
                        'path': subcat['key'],
                        'ismultiple': subcat['ismultiple'],
                        'attributes': list(self.generate_category_attributes(subcat)),
                        'display': self.resolve_display(subcat.names, language_code=self.use_language_code)
                    }
                    new_prefix = subcat["key"]
                yield from self.generate_category_paths(subcat, prefix=new_prefix)

    def generate_attributes(self, root):
        if hasattr(root, 'attribute'):
            for attribute in root.attribute:

                if attribute['type'] == 'LIST':
                    options = list(self.get_list_options(attribute))
                elif attribute['type'] == 'TREE':
                    options = list(self.get_tree_options(attribute))
                else:
                    options = None

                yield {
                    'key': attribute['key'],
                    'type': attribute['type'],
                    'isrequired': attribute['isrequired'] == 'true',
                    'display': self.resolve_display(attribute.names, language_code=self.use_language_code),
                    'options': options
                }

    def resolve_display(self, items, language_code='en'):
        for item in items:
            if item['language_code'] == language_code:
                return item['value']
        else:
            return 'n/a'


class Names(BaseModel):
    name: str
    locale: Optional[str]


class ListOptions(BaseModel):
    id: str
    names: List[Names]


class PatrolMetaData(BaseModel):
    id: str
    names: List[Names]
    requiredWhen: Optional[str] = 'False'
    listOptions: Optional[List[ListOptions]] = None
    type: str


class PatrolDataModel(BaseModel):
    patrolMetadata: List[PatrolMetaData]




