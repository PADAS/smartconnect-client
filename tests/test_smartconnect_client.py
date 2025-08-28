import json
import uuid
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import pytest
import httpx
import pytz
from pydantic import parse_obj_as

from smartconnect import SmartClient
from smartconnect.exceptions import (
    SMARTClientException, 
    SMARTClientServerError, 
    SMARTClientClientError, 
    SMARTClientServerUnreachableError, 
    SMARTClientUnauthorizedError
)
from smartconnect.models import (
    ConservationArea, 
    DataModel, 
    ConfigurableDataModel, 
    PatrolDataModel, 
    Patrol, 
    SMARTResponse,
    SmartConnectApiInfo
)


class TestSmartClientInitialization:
    """Test SmartClient initialization and configuration."""
    
    def test_init_with_valid_parameters(self):
        """Test SmartClient initialization with valid parameters."""
        client = SmartClient(
            api="https://test.example.com",
            username="testuser",
            password="testpass",
            use_language_code="en",
            version="7.5"
        )
        
        assert client.api == "https://test.example.com"
        assert client.username == "testuser"
        assert client.password == "testpass"
        assert client.use_language_code == "en"
        assert client.version == "7.5"
        assert client.verify_ssl is not None
        assert client.max_retries is not None
        assert client._session is not None
    
    def test_init_removes_trailing_slash(self):
        """Test that trailing slash is removed from API URL."""
        client = SmartClient(
            api="https://test.example.com/",
            username="testuser",
            password="testpass"
        )
        
        assert client.api == "https://test.example.com"
    
    def test_init_with_defaults(self):
        """Test SmartClient initialization with default values."""
        client = SmartClient(
            api="https://test.example.com",
            username="testuser",
            password="testpass"
        )
        
        assert client.use_language_code == "en"
        assert client.version == "7.5"


class TestSmartClientAuthentication:
    """Test SmartClient authentication methods."""
    
    @pytest.fixture
    def client(self):
        return SmartClient(
            api="https://test.example.com",
            username="testuser",
            password="testpass"
        )
    
    def test_ensure_login_with_existing_session(self, client):
        """Test ensure_login when session already has JSESSIONID."""
        # Mock existing session with JSESSIONID
        mock_cookie = Mock()
        mock_cookie.name = "JSESSIONID"
        mock_cookie.value = "existing-session-id"
        
        client._session.cookies = {"JSESSIONID": mock_cookie}
        
        result = client.ensure_login()
        assert result == client._session
    
    @patch('httpx.Client.get')
    @patch('httpx.Client.post')
    def test_ensure_login_successful(self, mock_post, mock_get, client):
        """Test successful login flow."""
        # Mock landing page response
        mock_landing_response = Mock()
        mock_landing_response.is_success = True
        mock_get.return_value = mock_landing_response
        
        # Mock login response
        mock_login_response = Mock()
        mock_login_response.is_success = True
        mock_post.return_value = mock_login_response
        
        result = client.ensure_login()
        assert result == client._session
        
        # Verify calls were made
        mock_get.assert_called_once_with('https://test.example.com/connect/home')
        mock_post.assert_called_once_with(
            'https://test.example.com/j_security_check',
            data={"j_username": "testuser", "j_password": "testpass"}
        )
    
    @patch('httpx.Client.get')
    def test_ensure_login_landing_page_failure(self, mock_get, client):
        """Test login failure when landing page is unreachable."""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.url = "https://test.example.com/connect/home"
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(SMARTClientServerUnreachableError):
            client.ensure_login()
    
    @patch('httpx.Client.get')
    @patch('httpx.Client.post')
    def test_ensure_login_unauthorized(self, mock_post, mock_get, client):
        """Test login failure with 401 unauthorized."""
        # Mock landing page response
        mock_landing_response = Mock()
        mock_landing_response.is_success = True
        mock_get.return_value = mock_landing_response
        
        # Mock login response with 401
        mock_login_response = Mock()
        mock_login_response.is_success = False
        mock_login_response.is_redirect = False
        mock_login_response.status_code = 401
        mock_login_response.url = "https://test.example.com/j_security_check"
        mock_post.return_value = mock_login_response
        
        with pytest.raises(SMARTClientUnauthorizedError):
            client.ensure_login()
    
    @patch('httpx.Client.get')
    @patch('httpx.Client.post')
    def test_ensure_login_client_error(self, mock_post, mock_get, client):
        """Test login failure with client error."""
        # Mock landing page response
        mock_landing_response = Mock()
        mock_landing_response.is_success = True
        mock_get.return_value = mock_landing_response
        
        # Mock login response with client error
        mock_login_response = Mock()
        mock_login_response.is_success = False
        mock_login_response.is_redirect = False
        mock_login_response.is_client_error = True
        mock_login_response.status_code = 400
        mock_login_response.url = "https://test.example.com/j_security_check"
        mock_login_response.text = "Bad request"
        mock_post.return_value = mock_login_response
        
        with pytest.raises(SMARTClientClientError):
            client.ensure_login()


class TestSmartClientAPICalls:
    """Test SmartClient API call methods."""
    
    @pytest.fixture
    def client(self):
        return SmartClient(
            api="https://test.example.com",
            username="testuser",
            password="testpass"
        )
    
    @patch.object(SmartClient, 'ensure_login')
    @patch('httpx.Client.get')
    def test_get_server_api_info(self, mock_get, mock_ensure_login, client):
        """Test getting server API info."""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "version": "7.5",
            "features": ["feature1", "feature2"]
        }
        mock_get.return_value = mock_response
        
        result = client.get_server_api_info()
        
        assert isinstance(result, SmartConnectApiInfo)
        mock_ensure_login.assert_called_once()
        mock_get.assert_called_once_with(
            'https://test.example.com/api/info',
            headers={'accept': 'application/json'}
        )
    
    @patch.object(SmartClient, 'ensure_login')
    @patch('httpx.Client.get')
    def test_get_conservation_areas(self, mock_get, mock_ensure_login, client):
        """Test getting conservation areas."""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = [
            {
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "label": "Test CA",
                "status": "active",
                "revision": 1,
                "description": "Test Conservation Area"
            }
        ]
        mock_get.return_value = mock_response
        
        result = client.get_conservation_areas()
        
        assert len(result) == 1
        assert isinstance(result[0], ConservationArea)
        assert result[0].uuid == uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        assert result[0].label == "Test CA"
        assert result[0].status == "active"
        assert result[0].revision == 1
        mock_ensure_login.assert_called_once()
    
    @patch.object(SmartClient, 'ensure_login')
    @patch('httpx.Client.get')
    def test_list_configurable_datamodels(self, mock_get, mock_ensure_login, client):
        """Test listing configurable data models."""
        ca_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = [
            {
                "uuid": "456e7890-e89b-12d3-a456-426614174000",
                "name": "Test Model",
                "description": "Test Configurable Model"
            }
        ]
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_get.return_value = mock_response
        
        result = client.list_configurable_datamodels(ca_uuid=ca_uuid)
        
        assert result == mock_response.json.return_value
        mock_ensure_login.assert_called_once()
        mock_get.assert_called_once_with(
            'https://test.example.com/api/metadata/configurablemodel',
            params={"ca_uuid": ca_uuid},
            headers={'accept': 'application/json'}
        )
    
    @patch.object(SmartClient, 'ensure_login')
    @patch('httpx.Client.get')
    def test_download_configurable_datamodel(self, mock_get, mock_ensure_login, client):
        """Test downloading configurable data model."""
        cm_uuid = "456e7890-e89b-12d3-a456-426614174000"
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <datamodel>
            <category path="test" display="Test Category">
                <attribute key="test_attr" type="string" display="Test Attribute"/>
            </category>
        </datamodel>"""
        
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.text = open('tests/data/sample-configurablemodel.xml').read()
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_get.return_value = mock_response
        
        result = client.download_configurable_datamodel(cm_uuid=cm_uuid)
        
        assert isinstance(result, ConfigurableDataModel)
        assert result.cm_uuid == cm_uuid
        mock_ensure_login.assert_called_once()
        mock_get.assert_called_once_with(
            f'https://test.example.com/api/metadata/configurablemodel/{cm_uuid}',
            headers={'accept': 'application/xml'}
        )
    
    @patch.object(SmartClient, 'ensure_login')
    @patch('httpx.Client.get')
    def test_download_datamodel(self, mock_get, mock_ensure_login, client):
        """Test downloading data model."""
        ca_uuid = "123e4567-e89b-12d3-a456-426614174000"
        xml_content = open('tests/data/datamodel.xml').read()
        
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.text = xml_content
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_get.return_value = mock_response
        
        result = client.download_datamodel(ca_uuid=ca_uuid)
        
        assert isinstance(result, DataModel)
        mock_ensure_login.assert_called_once()
        mock_get.assert_called_once_with(
            f'https://test.example.com/api/metadata/datamodel/{ca_uuid}',
            headers={'accept': 'application/xml'}
        )
    
    # @patch.object(SmartClient, 'ensure_login')
    # @patch('httpx.Client.get')
    # def test_download_patrolmodel(self, mock_get, mock_ensure_login, client):
    #     """Test downloading patrol model."""
    #     ca_uuid = "123e4567-e89b-12d3-a456-426614174000"
    #     patrol_data = {
    #         "patrols": [
    #             {
    #                 "uuid": "789e0123-e89b-12d3-a456-426614174000",
    #                 "name": "Test Patrol"
    #             }
    #         ]
    #     }
        
    #     mock_response = Mock()
    #     mock_response.is_success = True
    #     mock_response.json.return_value = patrol_data
    #     mock_get.return_value = mock_response
        
    #     result = client.download_patrolmodel(ca_uuid=ca_uuid)
        
    #     assert isinstance(result, PatrolDataModel)
    #     mock_ensure_login.assert_called_once()
    #     mock_get.assert_called_once_with(
    #         f'https://test.example.com/api/metadata/patrol/{ca_uuid}',
    #         headers={'accept': 'application/json'}
    #     )
    
    # @patch.object(SmartClient, 'ensure_login')
    # @patch('httpx.Client.get')
    # def test_get_patrol(self, mock_get, mock_ensure_login, client):
    #     """Test getting patrol by ID."""
    #     patrol_id = "test-patrol-id"
    #     patrol_data = [{
    #         "uuid": "789e0123-e89b-12d3-a456-426614174000",
    #         "name": "Test Patrol",
    #         "startTime": "2023-01-01T10:00:00"
    #     }]
        
    #     mock_response = Mock()
    #     mock_response.is_success = True
    #     mock_response.json.return_value = patrol_data
    #     mock_get.return_value = mock_response
        
    #     result = client.get_patrol(patrol_id=patrol_id)
        
    #     assert isinstance(result, Patrol)
    #     assert result.uuid == uuid.UUID("789e0123-e89b-12d3-a456-426614174000")
    #     mock_ensure_login.assert_called_once()
    #     mock_get.assert_called_once_with(
    #         'https://test.example.com/api/query/custom/patrol',
    #         params={"client_patrol_uuid": patrol_id}
    #     )
    
    # @patch.object(SmartClient, 'ensure_login')
    # @patch('httpx.Client.get')
    # def test_get_patrol_waypoints(self, mock_get, mock_ensure_login, client):
    #     """Test getting patrol waypoints."""
    #     patrol_id = "test-patrol-id"
    #     waypoint_data = [{
    #         "type": "Feature",
    #         "geometry": {"coordinates": [123.45, -67.89], "type": "Point"},
    #         "properties": {
    #             "dateTime": "2023-01-01T10:00:00",
    #             "smartDataType": "patrol",
    #             "smartFeatureType": "waypoint",
    #             "smartAttributes": {
    #                 "waypoint": {
    #                     "uuid": "waypoint-123",
    #                     "name": "Test Waypoint"
    #                 }
    #             }
    #         }
    #     }]
        
    #     mock_response = Mock()
    #     mock_response.is_success = True
    #     mock_response.json.return_value = waypoint_data
    #     mock_get.return_value = mock_response
        
    #     result = client.get_patrol_waypoints(patrol_id=patrol_id)
        
    #     assert len(result) == 1
    #     assert result[0]["uuid"] == "waypoint-123"
    #     mock_ensure_login.assert_called_once()
    #     mock_get.assert_called_once_with(
    #         'https://test.example.com/api/query/custom/waypoint/patrol',
    #         params={"client_patrol_uuid": patrol_id}
    #     )
    
    @patch.object(SmartClient, 'ensure_login')
    @patch('httpx.Client.get')
    def test_get_incident(self, mock_get, mock_ensure_login, client):
        """Test getting incident by UUID."""
        incident_uuid = "test-incident-uuid"
        incident_data = [{
            "type": "Feature",
            "geometry": {"coordinates": [123.45, -67.89], "type": "Point"},
            "properties": {
                "fid": incident_uuid
            }
        }]
        
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = incident_data
        mock_get.return_value = mock_response
        
        result = client.get_incident(incident_uuid=incident_uuid)
        
        assert len(result) == 1
        assert isinstance(result[0], SMARTResponse)
        mock_ensure_login.assert_called_once()
        mock_get.assert_called_once_with(
            'https://test.example.com/api/query/custom/waypoint/incident',
            params={"client_incident_uuid": incident_uuid}
        )
    
    @patch.object(SmartClient, 'ensure_login')
    @patch('httpx.Client.post')
    def test_post_smart_request(self, mock_post, mock_ensure_login, client):
        """Test posting SMART request."""
        ca_uuid = "123e4567-e89b-12d3-a456-426614174000"
        request_data = {
            "type": "Feature",
            "geometry": {"coordinates": [123.45, -67.89], "type": "Point"},
            "properties": {
                "dateTime": "2023-01-01T10:00:00",
                "smartDataType": "incident",
                "smartFeatureType": "waypoint/new",
                "smartAttributes": {}
            }
        }
        
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.content = b"Success"
        mock_post.return_value = mock_response
        
        client.post_smart_request(json=json.dumps(request_data), ca_uuid=ca_uuid)
        
        mock_ensure_login.assert_called_once()
        mock_post.assert_called_once_with(
            f'https://test.example.com/api/data/{ca_uuid}',
            headers={'content-type': 'application/json'},
            data=json.dumps(request_data)
        )
    
    @patch.object(SmartClient, 'ensure_login')
    @patch('httpx.Client.post')
    def test_post_smart_request_failure(self, mock_post, mock_ensure_login, client):
        """Test posting SMART request failure."""
        ca_uuid = "123e4567-e89b-12d3-a456-426614174000"
        request_data = {"test": "data"}
        
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_response.content = b"Server Error"
        mock_response.url = f'https://test.example.com/api/data/{ca_uuid}'
        mock_post.return_value = mock_response
        
        with pytest.raises(SMARTClientException):
            client.post_smart_request(json=json.dumps(request_data), ca_uuid=ca_uuid)


class TestSmartClientCaching:
    """Test SmartClient caching functionality."""
    
    @pytest.fixture
    def client(self):
        return SmartClient(
            api="https://test.example.com",
            username="testuser",
            password="testpass"
        )
    
    @patch('smartconnect.cache.cache')
    @patch.object(SmartClient, 'get_conservation_areas')
    @patch.object(SmartClient, 'ensure_login')
    def test_get_conservation_area_with_cache_hit(self, mock_ensure_login, mock_get_cas, mock_cache, client):
        """Test getting conservation area with cache hit."""
        ca_uuid = "123e4567-e89b-12d3-a456-426614174000"
        cached_data = json.dumps({
            "uuid": ca_uuid,
            "label": "Cached CA",
            "status": "active",
            "revision": 1,
            "description": "Cached Conservation Area"
        })
        mock_cache.get.return_value = cached_data
        
        result = client.get_conservation_area(ca_uuid=ca_uuid)
        
        assert isinstance(result, ConservationArea)
        assert result.uuid == uuid.UUID(ca_uuid)
        assert result.label == "Cached CA"
        mock_cache.get.assert_called_once_with(f"cache:smart-ca:{ca_uuid}:metadata")
        mock_get_cas.assert_not_called()
    
    @patch('smartconnect.cache.cache')
    @patch.object(SmartClient, 'get_conservation_areas')
    @patch.object(SmartClient, 'ensure_login')
    def test_get_conservation_area_with_cache_miss(self, mock_ensure_login, mock_get_cas, mock_cache, client):
        """Test getting conservation area with cache miss."""
        ca_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_cache.get.return_value = None
        
        # Mock conservation areas response
        mock_ca = ConservationArea(
            label="Test CA",
            status="active",
            revision=1,
            uuid=uuid.UUID(ca_uuid),
            description="Test Conservation Area"
        )
        mock_get_cas.return_value = [mock_ca]
        
        result = client.get_conservation_area(ca_uuid=ca_uuid)
        
        assert result == mock_ca
        mock_cache.get.assert_called_once_with(f"cache:smart-ca:{ca_uuid}:metadata")
        mock_get_cas.assert_called_once()
        mock_cache.set.assert_called_once()
    
    @patch('smartconnect.cache.cache')
    def test_get_data_model_with_cache_hit(self, mock_cache, client):
        """Test getting data model with cache hit."""
        ca_uuid = "123e4567-e89b-12d3-a456-426614174000"
        cached_data = json.dumps({
            "datamodel": {"categories": []},
            "_categories": {},
            "_attributes": {}
        })
        mock_cache.get.return_value = cached_data
        
        result = client.get_data_model(ca_uuid=ca_uuid)
        
        assert isinstance(result, DataModel)
        mock_cache.get.assert_called_once_with(f"cache:smart-ca:{ca_uuid}:datamodel")
    
    def test_get_data_model_version_6(self):
        """Test getting data model for version 6 (returns blank model)."""
        client = SmartClient(
            api="https://test.example.com",
            username="testuser",
            password="testpass",
            version="6.5"
        )
        
        result = client.get_data_model(ca_uuid="test-uuid")
        
        assert isinstance(result, DataModel)


class TestSmartClientUtilityMethods:
    """Test SmartClient utility methods."""
    
    @pytest.fixture
    def client(self):
        return SmartClient(
            api="https://test.example.com",
            username="testuser",
            password="testpass"
        )
    
    def test_generate_patrol_label(self, client):
        """Test patrol label generation."""
        device_id = "test-device"
        ts = datetime(2023, 1, 15, 10, 30, 0, tzinfo=pytz.UTC)
        
        result = client.generate_patrol_label(device_id=device_id, prefix="wildlife", ts=ts)
        
        assert result == "wildlife/test-device/2023/01"
    
    def test_generate_patrol_label_without_timestamp(self, client):
        """Test patrol label generation without timestamp."""
        device_id = "test-device"
        
        with patch('smartconnect.datetime') as mock_datetime:
            mock_now = datetime(2023, 1, 15, 10, 30, 0, tzinfo=pytz.UTC)
            mock_datetime.now.return_value = mock_now
            
            result = client.generate_patrol_label(device_id=device_id, prefix="wildlife")
            
            assert result == "wildlife/test-device/2023/01"
    
    def test_load_datamodel_from_file(self, client, tmp_path):
        """Test loading data model from file."""
        datamodel_file = 'tests/data/datamodel.xml'
        result = client.load_datamodel(filename=datamodel_file)
        
        assert isinstance(result, DataModel)


class TestSmartClientErrorHandling:
    """Test SmartClient error handling."""
    
    @pytest.fixture
    def client(self):
        return SmartClient(
            api="https://test.example.com",
            username="testuser",
            password="testpass"
        )
    
    @patch.object(SmartClient, 'ensure_login')
    @patch('httpx.Client.get')
    def test_api_call_with_server_error(self, mock_get, mock_ensure_login, client):
        """Test API call with server error."""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception, match="Failed to download"):
            client.list_configurable_datamodels(ca_uuid="test-uuid")
    
    @patch.object(SmartClient, 'ensure_login')
    @patch('httpx.Client.get')
    def test_get_incident_with_failure(self, mock_get, mock_ensure_login, client):
        """Test getting incident with API failure."""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.content = b"Bad Request"
        mock_get.return_value = mock_response
        
        result = client.get_incident(incident_uuid="test-uuid")
        
        assert result is None
    
    def test_get_conservation_area_not_found(self, client):
        """Test getting conservation area that doesn't exist."""
        # Test that decorated method calls ensure_login
        with patch.object(client, 'ensure_login') as mock_ensure_login:
            with patch.object(client, 'get_conservation_areas') as mock_get_cas:
                mock_get_cas.return_value = []
                result = client.get_conservation_area(ca_uuid="non-existent-uuid")
                assert result is None


class TestSmartClientDecorators:
    """Test SmartClient decorators."""
    
    def test_with_login_session_decorator(self):
        """Test the with_login_session decorator."""
        client = SmartClient(
            api="https://test.example.com",
            username="testuser",
            password="testpass"
        )
        
        # Test that decorated method calls ensure_login
        with patch.object(client, 'ensure_login') as mock_ensure_login:
            with patch('httpx.Client.get') as mock_get:
                mock_response = Mock()
                mock_response.is_success = True
                mock_response.json.return_value = {
                    "build-date": "2023-01-01",
                    "build-version": "1.0.0",
                    "db-last-updated": "2023-01-01T10:00:00"
                }
                mock_get.return_value = mock_response
                
                client.get_server_api_info()
                mock_ensure_login.assert_called_once()
