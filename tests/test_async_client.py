import httpx
import pytest
import respx
from smartconnect import DataModel


@pytest.mark.asyncio
async def test_get_data_model(client_settings, smart_client, smart_ca_uuid, datamodel_response):
    # ToDo: mock cache
    async with respx.mock(assert_all_called=True) as smart_server_mock:
        # Mock datamodel request
        datamodel_url = f'{smart_client.api}/api/metadata/datamodel/{smart_ca_uuid}'
        smart_server_mock.get(datamodel_url).respond(
            status_code=206,
            text=datamodel_response
        )

        ca_datamodel = await smart_client.get_data_model(ca_uuid=smart_ca_uuid)
        assert ca_datamodel == DataModel().load(datamodel_response)
