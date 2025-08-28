import pytest
import respx
from smartconnect import SmartClient, SMARTClientException, SMARTClientUnauthorizedError, SMARTClientServerUnreachableError

def test_client_login(respx_mock):
    # Mock the login response
    respx_mock.post("https://fancyplace.smartconservationtools.org/server/j_security_check").mock(return_value=respx.MockResponse(200))

    respx_mock.get(
        "https://fancyplace.smartconservationtools.org/server/connect/home").mock(return_value=respx.MockResponse(200))

    smart_client = SmartClient(
        api="https://fancyplace.smartconservationtools.org/server",
        username="Earthranger",
        password="afancypassword"
    )

    # Perform the login
    session = smart_client.ensure_login()

    # Check if login was successful
    assert session is not None

def test_client_login_negative(respx_mock):
    # Mock the login response
    respx_mock.post(
        "https://fancyplace.smartconservationtools.org/server/j_security_check").mock(return_value=respx.MockResponse(401))

    respx_mock.get(
        "https://fancyplace.smartconservationtools.org/server/connect/home").mock(return_value=respx.MockResponse(200))

    smart_client = SmartClient(
        api="https://fancyplace.smartconservationtools.org/server",
        username="Earthranger",
        password="afancypassword"
    )

    
    with pytest.raises(SMARTClientUnauthorizedError):
        # Perform the login
        smart_client.ensure_login()

def test_async_client_landing_page_server500(respx_mock):

    # Given a smart connect server is not reachable.
    respx_mock.get(
        "https://fancyplace.smartconservationtools.org/server/connect/home").mock(return_value=respx.MockResponse(500))

    smart_client = SmartClient(
        api="https://fancyplace.smartconservationtools.org/server",
        username="Earthranger",
        password="afancypassword"
    )

    with pytest.raises(SMARTClientServerUnreachableError):
        # Perform the login
        smart_client.ensure_login()
