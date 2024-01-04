import json

import pytest
from smartconnect import AsyncSmartClient


@pytest.fixture
def client_settings():
    return {
        "api": "https://smarttestserverconnect.smartconservationtools.org/server",
        "username": "fake-username",
        "password": "fake-password"
    }


@pytest.fixture
def mock_cache(mocker):
    mock_cache = mocker.MagicMock()
    mock_cache.get.return_value = None
    mock_cache_module = mocker.MagicMock()
    mock_cache_module.cache = mock_cache
    return mock_cache_module


@pytest.fixture
def smart_client(client_settings):
    return AsyncSmartClient(**client_settings)


@pytest.fixture
def smart_ca_uuid():
    return "123ac748-6e05-4299-892f-335d21fd4ce6"


@pytest.fixture
def datamodel_response():
    with open("tests/test_datamodel.xml", "r") as f:
        text = f.read()
    return text


@pytest.fixture
def cas_response():
    with open("tests/test_cas.json", "r") as f:
        cas_json = json.loads(f.read())
    return cas_json


@pytest.fixture
def incident_response():
    return {}


@pytest.fixture
def incident_response_400():
    return {"error": "Exactly one query filter must be provided", "status": 400}


@pytest.fixture
def new_incident_response():
    return {'message': 'Created or updated 1 Independent Incidents (133) ', 'warnings': None}


@pytest.fixture
def new_patrol_response():
    return {}


@pytest.fixture
def new_track_point_response():
    return {}
