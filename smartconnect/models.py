from datetime import datetime, timedelta, timezone
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


class SmartAttributes(BaseModel):
    observationGroups: List[SmartObservationGroup]


class IncidentProperties(BaseModel):
    dateTime: datetime
    smartDataType: str = 'incident'
    smartFeatureType: str = 'observation'
    smartAttributes: SmartAttributes

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

SMARTCONNECT_DATFORMAT = '%Y-%m-%dT%H:%M:%S'

class ConservationArea(BaseModel):
    label: str
    status: str
    version: uuid.UUID
    revision: int
    description: str
    designation: str
    organization: str
    pointOfContact: str
    location: str
    owner: str
    caBoundaryJson: str = Field(None, description='A string containing GeoJSON')
    administrativeAreasJson: Optional[Any]
    uuid: uuid.UUID