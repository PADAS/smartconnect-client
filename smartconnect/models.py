from datetime import datetime, timedelta, timezone, date
import pytz
from pydantic import BaseModel, Field
from typing import List,Dict, Any, Optional
from enum import Enum
import uuid

class TransformationRule(BaseModel):

    match_pattern: dict
    transforms: dict


class SmartObservation(BaseModel):
    category: str
    attributes: dict


class SmartObservationGroup(BaseModel):
    observations: List[SmartObservation]


class IncidentSmartAttributes(BaseModel):
    observationGroups: Optional[List[SmartObservationGroup]]
    comment: Optional[str]





class IncidentProperties(BaseModel):
    dateTime: datetime
    smartDataType: str = 'incident'
    smartFeatureType: str = 'observation'
    smartAttributes: IncidentSmartAttributes

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime(SMARTCONNECT_DATFORMAT)
        }


class Geometry(BaseModel):
    coordinates: List[float] = Field(..., max_item=2, min_items=2)


class IndependentIncident(BaseModel):
    type: str = 'Feature'
    geometry: Geometry
    properties: IncidentProperties


class PatrolSmartAttributes(BaseModel):
    patrolUuid: Optional[str]
    patrolLegUuid: Optional[str]
    team: Optional[str]
    objective: Optional[str]
    comment: Optional[str]
    isArmed: Optional[str]
    transportType: Optional[str]
    mandate: Optional[str]
    number: Optional[int]
    members: Optional[List[str]]
    leader: Optional[str]


class PatrolProperties(BaseModel):
    dateTime: datetime
    smartDataType: str = 'patrol'
    smartFeatureType: str = 'patrol'
    smartAttributes: PatrolSmartAttributes

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime(SMARTCONNECT_DATFORMAT)
        }


class PatrolRequest(BaseModel):
    type: str = 'Feature'
    geometry: Geometry
    properties: PatrolProperties


class WaypointSmartAttributes(BaseModel):
    patrolUuid: str
    patrolLegUuid: str


class WaypointProperties(BaseModel):
    dateTime: datetime
    smartDataType: str = 'patrol'
    smartFeatureType: str = 'waypoint/new'
    smartAttributes: WaypointSmartAttributes

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime(SMARTCONNECT_DATFORMAT)
        }


class WaypointRequest(BaseModel):
    type: str = 'Feature'
    geometry: Geometry
    properties: WaypointProperties


class Waypoint(BaseModel):
    attachments: List[Any] # test what is contained here
    conservation_area_uuid: str
    date: date
    id: str
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
    attributes: Optional[List[Any]] # Need to test what values are in here
    client_uuid: str
    comment: str
    conservation_area: dict
    end_date: date
    id: str
    start_date: date
    team: dict
    uuid: str



class PatrolResponseProperties(BaseModel):
    fid: str
    patrol: Patrol
    patrol_leg: PatrolLeg
    waypoint: Waypoint


class PatrolResponse(BaseModel):
    type: str = 'Feature'
    geometry: Geometry
    properties: PatrolResponseProperties



SMARTCONNECT_DATFORMAT = '%Y-%m-%dT%H:%M:%S'

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


class SMARTRequest(BaseModel):
    patrol_requests : Optional[List[PatrolRequest]]
    waypoint_requests : Optional[List[WaypointRequest]]

    # class Config:
    #     arbitrary_types_allowed = True