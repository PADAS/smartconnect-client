import pytest
import respx
import httpx
from smartconnect import AsyncSmartClient, SMARTClientException

@pytest.mark.asyncio
@respx.mock
async def test_async_client_login():
    # Mock the login response
    respx.post(
        "https://fancyplace.smartconservationtools.org/server/j_security_check"
    ).respond(status_code=200)

    respx.get(
        "https://fancyplace.smartconservationtools.org/server/connect/home").respond(status_code=200)

    smart_client = AsyncSmartClient(
        api="https://fancyplace.smartconservationtools.org/server",
        username="Earthranger",
        password="afancypassword"
    )

    # Perform the login
    session = await smart_client.ensure_login()

    # Check if login was successful
    assert session is not None

@pytest.mark.asyncio
@respx.mock
async def test_async_client_login_negative():
    # Mock the login response
    respx.post(
        "https://fancyplace.smartconservationtools.org/server/j_security_check"
    ).respond(status_code=401)

    respx.get(
        "https://fancyplace.smartconservationtools.org/server/connect/home").respond(status_code=200)

    smart_client = AsyncSmartClient(
        api="https://fancyplace.smartconservationtools.org/server",
        username="Earthranger",
        password="afancypassword"
    )

    
    with pytest.raises(SMARTClientException):
        # Perform the login
        await smart_client.ensure_login()
