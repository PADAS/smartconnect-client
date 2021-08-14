from datetime import datetime, timedelta, timezone
import pytz
from pydantic import BaseModel, Field
from typing import List,Dict, Any
from enum import Enum

from models import TransformationRule, SmartAttributes, SmartObservation, SMARTCONNECT_DATFORMAT, \
 SmartObservationGroup, IncidentProperties, IndependentIncident
class TransformationRule(BaseModel):

    match_pattern: dict
    transforms: dict


class Transformer:

    def __init__(self, rule: TransformationRule):
        self.rule = rule

    def match(self, er_report):
        return er_report['event_type'] == self.match_pattern['event_type']

    def transform(self, er_report):
        return er_report


transformers = [
]


def matches(er_report: dict, transformer: dict):
    return er_report['event_type'] == transformer['event_type']


def match_transformer(er_report):

    for transformer in transformers:
        if matches(er_report, transformer):
            break
    else:
        transformer = None

    return transformer


class Transformer:
    def transform(self, *, er_report: dict, ca_uuid: str = None):

        present = datetime.now(tz=pytz.utc)

        longitude = er_report
        incident_data = {
            'type': 'Feature',
            'geometry': {
                'coordinates': [-122.5, 48.5],
                'type': 'Point',
            },

            'properties': {
                'dateTime': present.strftime(SMARTCONNECT_DATFORMAT),
                'smartDataType': 'incident',
                'smartFeatureType': 'observation',
                'smartAttributes': {
                    'observationGroups': [
                        {
                            'observations': [
                                {
                                    'category': 'animals.carcass',
                                    'attributes': {
                                        'causeofdeath': 'natural.depression',
                                        # 'species': 'chordata_rl.reptilia_rl.squamata_rl.amphisbaenidae_rl.blanus_rl.blanuscinereus_rl61469',
                                        # .loxodontaafricana_rl12392'
                                        'species': 'chordata_rl.mammalia_rl.proboscidea_rl.elephantidae_rl.loxodonta_rl',
                                    },

                                }
                            ]
                        }
                    ]

                }
            }
        }

        incident = IndependentIncident.parse_obj(incident_data)

        return incident

