from time import strptime
from typing import List

import requests
from pydantic.tools import parse_obj_as
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone
import pytz

import json
from dasclient.dasclient import DasClient

from smartconnect import SmartClient, utils
from smartconnect.er_sync_utils import build_earthranger_event_types, er_event_type_schemas_equal, \
    get_subjects_from_patrol_data_model, ERSubject, er_subjects_equal, build_earthranger_event_types_from_cdm

# Testing CA: Sintegrate at connect7.refractions.net:8443/server/connect/home
# CA_UUID = '8f7fbe1b-201a-4ef4-bda8-14f5581e65ce'
CA_LABEL = 'Smart ER Integration Test CA [SMART_ER]'


def test_get_conservation_area():
    smart_client = SmartClient(api='https://connect7.refractions.net:8443/server/', username='james.goodheart', password='apitesting1', use_language_code='en')
    das_client = DasClient(service_root='https://cdip-er.pamdas.org/api/v1.0',
                          username='',
                          password='',
                          token='asdfasdifuasdofpiausdfopasuidfpuoiasdf',
                          token_url=f"https://cdip-er.pamdas.org/oauth2/token",
                          client_id="das_web_client",
                          provider_key='smart')

    # caslist = smart_client.get_conservation_areas()
    #
    # for ca in caslist:
    #     if ca.label == CA_LABEL:
    #         ca_uuid = ca.uuid
    #         break

    # print(f'CA UUID: {ca_uuid}')
    # predicted_timezone = utils.guess_ca_timezone(ca)
    # print(f'{ca.label} -- Predicted_timezone: {predicted_timezone}')
    #
    # present = datetime.now(tz=pytz.utc)
    # print(f'Now is: {present.astimezone(predicted_timezone)} in {predicted_timezone}')

    ca_uuid = '8a0a2bea-13ed-4cc7-8f76-1717347ea18a'

    dm = smart_client.download_datamodel(ca_uuid=ca_uuid)
    dm_dict = dm.export_as_dict()

    event_types = build_earthranger_event_types(dm_dict)

    existing_event_categories = das_client.get_event_categories()
    event_category = next((x for x in existing_event_categories if x.get('value') == CA_LABEL[0:40]), None)
    if not event_category:
        event_category = dict(value=CA_LABEL[0:40],
                              display=CA_LABEL[0:40])
        das_client.post_event_category(event_category)

    existing_event_types = das_client.get_event_types()
    try:
        for event_type in event_types:
            event_type_match = next((x for x in existing_event_types if x.get('value') == event_type.get('value')), None)
            if event_type_match:
                event_type_match_schema = das_client.get_event_schema(event_type.get('value'))
                if not er_event_type_schemas_equal(json.loads(event_type.get('schema')), event_type_match_schema):
                    # TODO: Update Das Client to update event type
                    pass
            else:
                event_type['category'] = event_category.get('value')
                das_client.post_event_type(event_type)
    except Exception as e:
        print(f'Exception raised posting event type {e}')
        print(dict(event_type=event_type))

    # smart_client.download_patrolmodel(ca_uuid=ca_uuid)
    # smart_client.download_missionmodel(ca_uuid=ca_uuid)
    #
    # present = datetime.now(tz=pytz.utc)
    #
    # smart_client.add_incident(ca_uuid=ca_uuid)
    # smart_client.add_patrol_trackpoint(ca_uuid=ca_uuid, device_id='dev-00009', x=-122.4526, y=48.4948, timestamp=present)
    # smart_client.add_mission(ca_uuid=ca_uuid)

def download_patrol_datamodel():
    smart_client = SmartClient(api='http://connect7.refractions.net:8443/server/', username='james.goodheart', password='apitesting1', use_language_code='en')

    ca_uuid = '8a0a2bea-13ed-4cc7-8f76-1717347ea18a'

    pm = smart_client.download_patrolmodel(ca_uuid=ca_uuid)
    patrol_subjects = get_subjects_from_patrol_data_model(pm)

    das_client = DasClient(service_root='https://smart-er.pamdas.org/api/v1.0',
                           username='',
                           password='',
                           token='828eaa4ba81f87ac91ffcc105d6cf8b0ae5bb0aa76ce5565',
                           token_url=f"https://cdip-er.pamdas.org/oauth2/token",
                           client_id="das_web_client",
                           provider_key='smart')

    existing_subjects = parse_obj_as(List[Subject], das_client.get_subjects())
    for subject in patrol_subjects:
        smart_member_id = subject.additional.get('smart_member_id')
        existing_subject_match = next((ex_subject for ex_subject in existing_subjects
                                       if ex_subject.additional.get('smart_member_id') == smart_member_id), None)
        if existing_subject_match:
            subject.id = existing_subject_match.id
            if not er_subjects_equal(subject, existing_subject_match):
                pass
                # TODO: subject updates
                # das_client.patch_subject(subject.dict())
        else:
            subject_dict = subject.dict()
            # can't pass None value for id when posting new subjects
            if 'id' in subject_dict.keys():
                del subject_dict['id']
            das_client.post_subject(subject_dict)


def add_patrol():
    smart_client = SmartClient(api='https://connect7.refractions.net:8443/server', username='james.goodheart',
                               password='apitesting1', use_language_code='en')
    smart_client.add_patrol(ca_uuid="8a0a2bea-13ed-4cc7-8f76-1717347ea18a",
                                       patrol_uuid="a9766a42-3541-47be-973a-c48a12039c7d",
                                       patrol_leg_uuid="bb80030a-b572-4e50-ade5-c902a8cc9fdc",
                                       timestamp=datetime.fromisoformat("2022-03-25T09:16:27.823000-07:00"),
                                       x=-104.96092387932455,
                                       y=39.80896552541091)

def get_patrol():
    smart_client = SmartClient(api='https://connect7.refractions.net:8443/server', username='james.goodheart', password='apitesting1', use_language_code='en')
    smart_client.get_patrol(patrol_id='dd8bceb4-0597-400f-9fc1-11d6770f507c')

def get_track_points_for_patrol():
    smart_client = SmartClient(api='https://connect7.refractions.net:8443/server', username='james.goodheart', password='apitesting1', use_language_code='en')
    smart_client.get_patrsol_waypoints(patrol_id='c29fb89f-4fb2-4a71-84a2-aa9ec01c9ba5')

def add_trackpoint():
    smart_client = SmartClient(api='https://connect7.refractions.net:8443/server', username='james.goodheart', password='apitesting1', use_language_code='en')
    smart_client.add_patrol_trackpoint(ca_uuid="8a0a2bea-13ed-4cc7-8f76-1717347ea18a",
                                       patrol_uuid="a9766a42-3541-47be-973a-c48a12039c7d",
                                       patrol_leg_uuid="910f5c2f-59a3-4f71-beb7-28ceaf1b16f7",
                                       timestamp=datetime.fromisoformat("2022-03-28T09:16:27.823000-07:00"),
                                       x=-104.96092387932455,
                                       y=39.80896552541091)

def add_waypoint():
    smart_client = SmartClient(api='https://connect7.refractions.net:8443/server', username='james.goodheart', password='apitesting1', use_language_code='en')
    smart_client.add_patrol_waypoint(ca_uuid="8a0a2bea-13ed-4cc7-8f76-1717347ea18a",
                                       patrol_uuid="a9766a42-3541-47be-973a-c48a12039c7d",
                                       patrol_leg_uuid="910f5c2f-59a3-4f71-beb7-28ceaf1b16f7",
                                       timestamp=datetime.fromisoformat("2022-03-18T09:16:27.823000-07:00"),
                                       x=-104.96092387932455,
                                       y=39.80896552541091)

def download_datamodel():
    smart_client = SmartClient(api='https://pantheraearthrangertest.smartconservationtools.org/server', username='EarthRanger', password='EarthRanger', use_language_code='en')
    smart_client.get_data_model(ca_uuid="e71d62fe-43c2-418f-bd6f-2f6bb09807dc", force=True)

def download_configurable_datamodel():
    smart_client = SmartClient(api='https://pantheraearthrangertest.smartconservationtools.org/server', username='EarthRanger', password='EarthRanger', use_language_code='en')
    smart_client.get_configurable_data_model(cm_uuid="22f8ac6ccca04f2fba4361392f9bc8cb", force=True)

def build_earthranger_event_types_from_config_dm_test():
    ca_uuid="e71d62fe-43c2-418f-bd6f-2f6bb09807dc"
    smart_client = SmartClient(api='https://pantheraearthrangertest.smartconservationtools.org/server',
                               username='EarthRanger', password='EarthRanger', use_language_code='en')
    cm_uuid = smart_client.get_configurable_datamodel_for_ca(ca_uuid=ca_uuid)
    dm = smart_client.get_data_model(ca_uuid=ca_uuid, force=True)
    cdm = smart_client.get_configurable_data_model(cm_uuid=cm_uuid, force=True)
    if cdm and dm:
        event_types = build_earthranger_event_types_from_cdm(dm=dm.export_as_dict(), ca_uuid=ca_uuid, ca_identifier="test", cdm=cdm.export_as_dict())
        pass


def get_smart_connect_server_version():
    smart_client = SmartClient(api='https://pantheraearthrangertest.smartconservationtools.org/server',
                               username='EarthRanger', password='EarthRanger', use_language_code='en')
    version = smart_client.get_server_version()

if __name__ == '__main__':
    # test_get_conservation_area()
    # pm = download_patrol_datamodel()
    # add_trackpoint()
    # add_waypoint()
    # add_patrol()
    # get_patrol()
    # get_track_points_for_patrol()

    # download_datamodel()
    # download_configurable_datamodel()
    build_earthranger_event_types_from_config_dm_test()
    # get_smart_connect_server_version()

