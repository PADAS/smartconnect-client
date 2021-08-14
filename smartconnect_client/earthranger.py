from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field, validator
from typing import Any, Dict, Optional
from enum import Enum


import requests
import redis
import json

cache = redis.Redis(host='localhost', port=30091)

class StateEnum(str, Enum):
    active = 'active'
    closed = 'resolved'
    new = 'new'

class ERLocation(BaseModel):
    latitude: float
    longitude: float

class Event(BaseModel):
    location: ERLocation
    time: datetime
    serial_number: int
    event_type: str
    priority: int
    priority_label: str
    title: Optional[str]
    state: StateEnum 
    event_details: Dict[str, Any]

    @validator('state')
    def clean_sender(cls, val):
        if val == 'new':
            return 'active'
        return val


class Token(BaseModel):
    access_token: str
    token_type: str

class EREventsClient:
    
    def __init__(self, *, er_site=None, er_username=None, er_password=None):
        self.er_site = er_site
        self.er_username = er_username
        self.er_password = er_password

    def get_access_token(self):
        '''
        TODO: add caching
        '''
        response = requests.post(f'https://{self.er_site}/oauth2/token/', data={
            'grant_type': 'password', 'username': self.er_username,'password': self.er_password, 'client_id': 'das_web_client'
        })
        
        if response.ok:
            token_response = response.json()
            return Token.parse_obj(token_response)
        
    def get_events(self):
        ertoken = self.get_access_token()
        headers = {'accept': 'application/json',
                'authorization': f'{ertoken.token_type} {ertoken.access_token}'
        }

        FILTER_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ' 
        lower = datetime.now(tz=timezone.utc) - timedelta(days=1)
        upper = datetime.now(tz=timezone.utc) - timedelta(hours=1)

        event_filter_spec = {
            'create_date': {'lower': lower.strftime(FILTER_DATETIME_FORMAT), 'upper': upper.strftime(FILTER_DATETIME_FORMAT)}
        }

        print(f'Using filter: {event_filter_spec}')
        url = f'https://{self.er_site}/api/v1.0/activity/events?filter={json.dumps(event_filter_spec)}&sort_by=created_at'
        while True:

            print(f'Fetching for url: {url}')
            events_response = requests.get(url, headers=headers)
                                                
            events_response = events_response.json()                                       

            for event in events_response['data']['results']:
                yield Event.parse_obj(event)

            url = events_response['data']['next']
            if url is None:
                break

if __name__ == '__main__':

    for event in EREventsClient(er_site='develop.pamdas.org', er_username='chrisd', er_password='8adioTwit').get_events():
        print(event.serial_number)