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


class Geometry(BaseModel):
    coordinates: List[float] = Field(..., max_item=2, min_items=2)


class SmartAttributes(BaseModel):
    observationGroups: Optional[List[SmartObservationGroup]]
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



class SMARTResponseProperties(BaseModel):
    fid: str
    patrol: Optional[Patrol]
    patrol_leg: Optional[PatrolLeg]
    waypoint: Optional[Waypoint]

class SMARTResponse(BaseModel):
    type: str = 'Feature'
    geometry: Geometry
    properties: SMARTResponseProperties



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


class SMARTCompositeRequest(BaseModel):
    patrol_requests : Optional[List[SMARTRequest]]
    waypoint_requests : Optional[List[SMARTRequest]]

    # class Config:
    #     arbitrary_types_allowed = True