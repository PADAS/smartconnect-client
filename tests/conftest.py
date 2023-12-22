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
def smart_client(client_settings):
    return AsyncSmartClient(**client_settings)


@pytest.fixture
def smart_ca_uuid():
    return "fake-ca-uuid"


@pytest.fixture
def datamodel_response():
    with open("tests/test_datamodel.xml", "r") as f:
        text = f.read()
    return text
