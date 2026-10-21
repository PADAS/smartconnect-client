import json

import httpx
import pytest
import respx
from pydantic.tools import parse_obj_as
from typing import List

from smartconnect import DataModel, models

# login_mock is for the requests to initiate a session and authenticate.
login_mock = respx.mock(base_url="https://smarttestserverconnect.smartconservationtools.org/server", assert_all_called=True)
# api_mock.get("/baz/", name="baz").mock(
#     return_value=httpx.Response(200, json={"name": "baz"}),)
login_mock.post('/j_security_check').respond(status_code=200)
login_mock.get('/connect/home').respond(status_code=200)

@pytest.mark.asyncio
@login_mock
async def test_get_data_model(
        client_settings, smart_client, smart_ca_uuid, datamodel_response,
        mocker, mock_cache
):
    mocker.patch("smartconnect.async_client.cache", mock_cache)
    async with respx.mock(assert_all_called=True) as smart_server_mock:
        # Mock api response for the datamodel endpoint
        datamodel_url = f'{smart_client.api}/api/metadata/datamodel/{smart_ca_uuid}'
        smart_server_mock.get(datamodel_url).respond(
            status_code=206,
            text=datamodel_response
        )

        ca_datamodel = await smart_client.get_data_model(ca_uuid=smart_ca_uuid)
        expected_datamodel = DataModel()
        expected_datamodel.load(datamodel_response)
        assert ca_datamodel.datamodel == expected_datamodel.datamodel
        assert ca_datamodel._categories == expected_datamodel._categories
        assert ca_datamodel._attributes == expected_datamodel._attributes
        # check that the datamodel was cached
        assert mock_cache.cache.set.called


@pytest.mark.asyncio
@login_mock
async def test_get_conservation_area(
        client_settings, smart_client, smart_ca_uuid, cas_response,
        mocker, mock_cache
):
    mocker.patch("smartconnect.async_client.cache", mock_cache)
    async with respx.mock(assert_all_called=True) as smart_server_mock:
        # Mock api response for the conservation area endpoint
        cas_url = f'{smart_client.api}/api/conservationarea'
        smart_server_mock.get(cas_url).respond(
            status_code=200,
            json=cas_response
        )
        conservation_area = await smart_client.get_conservation_area(ca_uuid=smart_ca_uuid)
        assert conservation_area == models.ConservationArea.parse_obj(cas_response[0])
        # check that the cas was cached
        assert mock_cache.cache.set.called


@pytest.mark.asyncio
@login_mock
async def test_get_incident_with_invalid_id(
        client_settings, smart_client, smart_ca_uuid, incident_response_400,
        mocker, mock_cache
):
    mocker.patch("smartconnect.async_client.cache", mock_cache)
    async with respx.mock(assert_all_called=True) as smart_server_mock:
        # Mock api response for the incident details endpoint
        incident_url = f'{smart_client.api}/api/query/custom/waypoint/incident'
        smart_server_mock.get(incident_url).respond(
            status_code=400,
            json=incident_response_400
        )
        response = await smart_client.get_incident(
            incident_uuid=None
        )
        assert response == None


@pytest.mark.asyncio
@login_mock
async def test_post_smart_request_incident(
        client_settings, smart_client, smart_ca_uuid, new_incident_response
):
    async with respx.mock(assert_all_called=True) as smart_server_mock:
        # Mock api response for the incident details endpoint
        data_url = f'{smart_client.api}/api/data/{smart_ca_uuid}'
        smart_server_mock.post(data_url).respond(
            status_code=200,
            json=new_incident_response
        )
        payload = {
            "type": "Feature",
            "geometry": {"coordinates": [123.745678, -6.54321]},
            "properties": {
                "dateTime": "2023-11-26T10:00:00",
                "smartDataType": "incident",
                "smartFeatureType": "waypoint/new",
                "smartAttributes": {
                    "observationGroups": [
                        {
                            "observations": [
                                {
                                    "observationUuid": "123427f7-4234-445c-aa4b-47694b4fc567    ",
                                    "category": "gfwgladalert",
                                    "attributes": {"confidence": 1.0}
                                }
                            ]
                        }
                    ],
                    "comment": "Report: GFW Integrated Deforestation Cluster (2 alerts)\nImported: 2023-12-27T00:38:30.006175+10:00",
                    "attachments": []
                }
            }
        }
        response = await smart_client.post_smart_request(
            json=payload,
            ca_uuid=smart_ca_uuid
        )
        assert response == new_incident_response


@pytest.mark.asyncio
@login_mock
async def test_post_smart_request_patrol(
        client_settings, smart_client, smart_ca_uuid, new_patrol_response
):
    # ToDo: Finish payload and mocks for this test
    async with respx.mock(assert_all_called=True) as smart_server_mock:
        # Mock api response for the incident details endpoint
        data_url = f'{smart_client.api}/api/data/{smart_ca_uuid}'
        smart_server_mock.post(data_url).respond(
            status_code=200,
            json=new_patrol_response
        )
        payload = {}
        response = await smart_client.post_smart_request(
            json=payload,
            ca_uuid=smart_ca_uuid
        )
        assert response == new_patrol_response


@pytest.mark.asyncio
@login_mock
async def test_post_smart_request_track_point(
        client_settings, smart_client, smart_ca_uuid, new_track_point_response
):
    # ToDo: Finish payload and mocks for this test
    async with respx.mock(assert_all_called=True) as smart_server_mock:
        # Mock api response for the incident details endpoint
        data_url = f'{smart_client.api}/api/data/{smart_ca_uuid}'
        smart_server_mock.post(data_url).respond(
            status_code=200,
            json=new_track_point_response
        )
        payload = {}
        response = await smart_client.post_smart_request(
            json=payload,
            ca_uuid=smart_ca_uuid
        )
        assert response == new_track_point_response


@pytest.mark.asyncio
async def test_get_data_model_cache_hit_does_not_login(
        smart_client, smart_ca_uuid, datamodel_response, mocker, mock_cache
):
    cached_datamodel = DataModel()
    cached_datamodel.load(datamodel_response)
    mock_cache.cache.get.return_value = json.dumps(cached_datamodel.export_as_dict())
    mocker.patch("smartconnect.async_client.cache", mock_cache)
    # Any HTTP request (including the login flow) fails the test.
    async with respx.mock(assert_all_mocked=True) as smart_server_mock:
        ca_datamodel = await smart_client.get_data_model(ca_uuid=smart_ca_uuid)
        assert not smart_server_mock.calls
    assert ca_datamodel._categories == cached_datamodel._categories


@pytest.mark.asyncio
async def test_get_configurable_data_model_cache_hit_does_not_login(
        smart_client, mocker, mock_cache
):
    cm_uuid = "b0ffbb1c-1b7a-4b1a-9c1d-1a0a2e8c1a11"
    mock_cache.cache.get.return_value = json.dumps(
        {"categories": [], "attributes": [], "name": "Cached CM", "cm_uuid": cm_uuid}
    )
    mocker.patch("smartconnect.async_client.cache", mock_cache)
    async with respx.mock(assert_all_mocked=True) as smart_server_mock:
        cdm = await smart_client.get_configurable_data_model(cm_uuid=cm_uuid)
        assert not smart_server_mock.calls
    assert cdm.cm_uuid == cm_uuid


@pytest.mark.asyncio
async def test_get_conservation_area_cache_hit_does_not_login(
        smart_client, smart_ca_uuid, cas_response, mocker, mock_cache
):
    mock_cache.cache.get.return_value = json.dumps(cas_response[0])
    mocker.patch("smartconnect.async_client.cache", mock_cache)
    async with respx.mock(assert_all_mocked=True) as smart_server_mock:
        conservation_area = await smart_client.get_conservation_area(ca_uuid=smart_ca_uuid)
        assert not smart_server_mock.calls
    assert conservation_area == models.ConservationArea.parse_obj(cas_response[0])


@pytest.mark.asyncio
async def test_get_data_model_cache_miss_logs_in_once(
        smart_client, smart_ca_uuid, datamodel_response, mocker, mock_cache
):
    mocker.patch("smartconnect.async_client.cache", mock_cache)
    async with respx.mock(base_url=smart_client.api, assert_all_called=True) as smart_server_mock:
        home = smart_server_mock.get('/connect/home').respond(status_code=200)
        login = smart_server_mock.post('/j_security_check').respond(
            status_code=200, headers={"set-cookie": "JSESSIONID=abc; Path=/"}
        )
        smart_server_mock.get(f'/api/metadata/datamodel/{smart_ca_uuid}').respond(
            status_code=200, text=datamodel_response
        )
        await smart_client.get_data_model(ca_uuid=smart_ca_uuid)
        await smart_client.get_data_model(ca_uuid=smart_ca_uuid)
    assert home.call_count == 1
    assert login.call_count == 1
