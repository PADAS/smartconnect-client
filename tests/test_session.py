import pytest
import requests, requests_mock
from smartconnect import SmartClient, SMARTClientException, SMARTClientUnauthorizedError, SMARTClientServerUnreachableError

def test_client_login(requests_mock):
    # Mock the login response
    requests_mock.post("https://fancyplace.smartconservationtools.org/server/j_security_check", status_code=200)

    requests_mock.get(
        "https://fancyplace.smartconservationtools.org/server/connect/home", status_code=200)

    smart_client = SmartClient(
        api="https://fancyplace.smartconservationtools.org/server",
        username="Earthranger",
        password="afancypassword"
    )

    # Perform the login
    session = smart_client.ensure_login()

    # Check if login was successful
    assert session is not None

def test_client_login_negative(requests_mock):
    # Mock the login response
    requests_mock.post(
        "https://fancyplace.smartconservationtools.org/server/j_security_check", status_code=401)

    requests_mock.get(
        "https://fancyplace.smartconservationtools.org/server/connect/home", status_code=200)

    smart_client = SmartClient(
        api="https://fancyplace.smartconservationtools.org/server",
        username="Earthranger",
        password="afancypassword"
    )

    
    with pytest.raises(SMARTClientUnauthorizedError):
        # Perform the login
        smart_client.ensure_login()

def test_async_client_landing_page_server500(requests_mock):

    # Given a smart connect server is not reachable.
    requests_mock.get(
        "https://fancyplace.smartconservationtools.org/server/connect/home", status_code=500)

    smart_client = SmartClient(
        api="https://fancyplace.smartconservationtools.org/server",
        username="Earthranger",
        password="afancypassword"
    )

    with pytest.raises(SMARTClientServerUnreachableError):
        # Perform the login
        smart_client.ensure_login()
