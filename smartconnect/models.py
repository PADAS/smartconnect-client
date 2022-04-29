import json
import uuid
from datetime import datetime, date
from typing import List, Any, Optional

import untangle
from pydantic import BaseModel, Field

SMARTCONNECT_DATFORMAT = '%Y-%m-%dT%H:%M:%S'


class TransformationRule(BaseModel):
    match_pattern: dict
    transforms: dict


class SmartObservation(BaseModel):
    category: str
    attributes: dict


class SmartObservationGroup(BaseModel):
    observations: List[SmartObservation]


class Geometry(BaseModel):
    coordinates: List[float] = Field(..., max_item=2, min_items=2)


class SmartAttributes(BaseModel):
    observationGroups: Optional[List[SmartObservationGroup]]
    patrolUuid: Optional[str]
    patrolLegUuid: Optional[str]
    patrolId: Optional[str]
    incidentUuid: Optional[str]
    team: Optional[str]
    objective: Optional[str]
    comment: Optional[str]
    isArmed: Optional[str]
    transportType: Optional[str]
    mandate: Optional[str]
    number: Optional[int]
    members: Optional[List[str]]
    leader: Optional[str]


class Properties(BaseModel):
    dateTime: datetime
    smartDataType: str
    smartFeatureType: str
    smartAttributes: SmartAttributes

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime(SMARTCONNECT_DATFORMAT)
        }


class SMARTRequest(BaseModel):
    type: str = 'Feature'
    geometry: Geometry
    properties: Properties


class Waypoint(BaseModel):
    attachments: List[Any] # test what is contained here
    conservation_area_uuid: str
    date: date
    id: str
    client_uuid: Optional[str]
    last_modified: datetime
    observation_groups: List[Any] # test
    raw_x: float
    raw_y: float
    source: str
    time: str


class PatrolLeg(BaseModel):
    client_uuid: str
    end_date: date
    id: str
    mandate: dict
    members: List[dict]
    start_date = date
    type: dict
    uuid: str


class Patrol(BaseModel):
    armed: bool
    attributes: Optional[List[Any]]  # Need to test what values are in here
    client_uuid: str
    comment: str
    conservation_area: dict
    end_date: date
    id: str
    start_date: date
    team: dict
    uuid: str


class SMARTResponseProperties(BaseModel):
    fid: str
    patrol: Optional[Patrol]
    patrol_leg: Optional[PatrolLeg]
    waypoint: Optional[Waypoint]


class SMARTResponse(BaseModel):
    type: str = 'Feature'
    geometry: Geometry
    properties: SMARTResponseProperties


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


class ConservationArea(BaseModel):
    label: str
    status: str
    version: Optional[uuid.UUID]
    revision: int
    description: Optional[str]
    designation: Optional[str]
    organization: Optional[str]
    pointOfContact: Optional[str]
    location: Optional[str]
    owner: Optional[str]
    caBoundaryJson: Optional[str] = Field(None, description='A string containing GeoJSON')
    administrativeAreasJson: Optional[Any]
    uuid: uuid.UUID


class SMARTCompositeRequest(BaseModel):
    ca_uuid: str
    patrol_requests: Optional[List[SMARTRequest]] = []
    waypoint_requests: Optional[List[SMARTRequest]] = []
    track_point_requests: Optional[List[SMARTRequest]] = []


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
        if hasattr(root, 'attributes'):
            for attribute in root.attributes:
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
