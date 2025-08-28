import json
import uuid
from datetime import datetime, date
import pytest
from pydantic import ValidationError

from smartconnect.models import (
    CategoryAttribute,
    Category,
    AttributeOption,
    Attribute,
    TransformationRule,
    SmartObservation,
    SmartObservationGroup,
    Geometry,
    File,
    SmartAttributes,
    Properties,
    SMARTRequest,
    SMARTResponse,
    Patrol,
    PatrolDataModel,
    PatrolMetaData,
    Names,
    DataModel,
    ConservationArea,
    ConfigurableDataModel,
    SmartConnectApiInfo,
    SMARTResponseProperties
)


class TestCategoryAttribute:
    """Test CategoryAttribute model."""
    
    def test_valid_category_attribute(self):
        """Test creating a valid CategoryAttribute."""
        attr = CategoryAttribute(key="test_key", is_active=True)
        
        assert attr.key == "test_key"
        assert attr.is_active is True
    
    def test_category_attribute_with_alias(self):
        """Test CategoryAttribute with alias field."""
        attr = CategoryAttribute(key="test_key", isactive=False)
        
        assert attr.key == "test_key"
        assert attr.is_active is False
    
    def test_category_attribute_defaults(self):
        """Test CategoryAttribute with default values."""
        attr = CategoryAttribute(key="test_key")
        
        assert attr.key == "test_key"
        assert attr.is_active is True


class TestCategory:
    """Test Category model."""
    
    def test_valid_category(self):
        """Test creating a valid Category."""
        category = Category(
            path="test/path",
            hkeyPath="test_hkey",
            display="Test Category",
            is_multiple=True,
            is_active=True,
            attributes=[
                CategoryAttribute(key="attr1"),
                CategoryAttribute(key="attr2", isactive=False)
            ]
        )
        
        assert category.path == "test/path"
        assert category.hkeyPath == "test_hkey"
        assert category.display == "Test Category"
        assert category.is_multiple is True
        assert category.is_active is True
        assert len(category.attributes) == 2
        assert category.attributes[0].key == "attr1"
        assert category.attributes[1].key == "attr2"
    
    def test_category_with_alias_fields(self):
        """Test Category with alias fields."""
        category = Category(
            path="test/path",
            hkeyPath="test_hkey",
            display="Test Category",
            ismultiple=True,
            isactive=False
        )
        
        assert category.is_multiple is True
        assert category.is_active is False
    
    def test_category_defaults(self):
        """Test Category with default values."""
        category = Category(
            path="test/path",
            hkeyPath="test_hkey",
            display="Test Category"
        )
        
        assert category.is_multiple is False
        assert category.is_active is True
        assert category.attributes is None


class TestAttributeOption:
    """Test AttributeOption model."""
    
    def test_valid_attribute_option(self):
        """Test creating a valid AttributeOption."""
        option = AttributeOption(
            key="option1",
            display="Option 1",
            is_active=True
        )
        
        assert option.key == "option1"
        assert option.display == "Option 1"
        assert option.is_active is True
    
    def test_attribute_option_with_alias(self):
        """Test AttributeOption with alias field."""
        option = AttributeOption(
            key="option1",
            display="Option 1",
            isActive=False
        )
        
        assert option.is_active is False
    
    def test_attribute_option_defaults(self):
        """Test AttributeOption with default values."""
        option = AttributeOption(key="option1", display="Option 1")
        
        assert option.is_active is True


class TestAttribute:
    """Test Attribute model."""
    
    def test_valid_attribute(self):
        """Test creating a valid Attribute."""
        attr = Attribute(
            key="test_attr",
            type="string",
            isrequired=True,
            display="Test Attribute",
            options=[
                AttributeOption(key="opt1", display="Option 1"),
                AttributeOption(key="opt2", display="Option 2")
            ]
        )
        
        assert attr.key == "test_attr"
        assert attr.type == "string"
        assert attr.isrequired is True
        assert attr.display == "Test Attribute"
        assert len(attr.options) == 2
    
    def test_attribute_defaults(self):
        """Test Attribute with default values."""
        attr = Attribute(
            key="test_attr",
            type="string",
            display="Test Attribute"
        )
        
        assert attr.isrequired is False
        assert attr.options is None


class TestTransformationRule:
    """Test TransformationRule model."""
    
    def test_valid_transformation_rule(self):
        """Test creating a valid TransformationRule."""
        rule = TransformationRule(
            match_pattern={"field": "value"},
            transforms={"field": "new_value"}
        )
        
        assert rule.match_pattern == {"field": "value"}
        assert rule.transforms == {"field": "new_value"}


class TestSmartObservation:
    """Test SmartObservation model."""
    
    def test_valid_smart_observation(self):
        """Test creating a valid SmartObservation."""
        observation = SmartObservation(
            observationUuid="123e4567-e89b-12d3-a456-426614174000",
            category="test_category",
            attributes={"key": "value"}
        )
        
        assert observation.observationUuid == "123e4567-e89b-12d3-a456-426614174000"
        assert observation.category == "test_category"
        assert observation.attributes == {"key": "value"}
    
    def test_smart_observation_with_none_uuid(self):
        """Test SmartObservation with None UUID."""
        value = dict(observationUuid="None",
                     category="test_category",
                     attributes={}
                     )
        observation = SmartObservation.parse_raw(json.dumps(value))
        
        assert observation.observationUuid is None


class TestSmartObservationGroup:
    """Test SmartObservationGroup model."""
    
    def test_valid_smart_observation_group(self):
        """Test creating a valid SmartObservationGroup."""
        group = SmartObservationGroup(
            observations=[
                SmartObservation(
                    observationUuid="123e4567-e89b-12d3-a456-426614174000",
                    category="test_category",
                    attributes={}
                )
            ]
        )
        
        assert len(group.observations) == 1
        assert group.observations[0].category == "test_category"


class TestGeometry:
    """Test Geometry model."""
    
    def test_valid_geometry(self):
        """Test creating a valid Geometry."""
        geometry = Geometry(coordinates=[123.45, -67.89])
        
        assert geometry.coordinates == [123.45, -67.89]
    
    def test_geometry_validation_too_few_coordinates(self):
        """Test Geometry validation with too few coordinates."""
        with pytest.raises(ValidationError):
            Geometry(coordinates=[123.45])
    
    def test_geometry_validation_too_many_coordinates(self):
        """Test Geometry validation with too many coordinates."""
        with pytest.raises(ValidationError):
            Geometry(coordinates=[123.45, -67.89, 100.0])


class TestFile:
    """Test File model."""
    
    def test_valid_file(self):
        """Test creating a valid File."""
        file_obj = File(
            filename="test.txt",
            data="base64_encoded_data",
            signatureType="md5"
        )
        
        assert file_obj.filename == "test.txt"
        assert file_obj.data == "base64_encoded_data"
        assert file_obj.signatureType == "md5"
    
    def test_file_without_signature(self):
        """Test File without signature type."""
        file_obj = File(
            filename="test.txt",
            data="base64_encoded_data"
        )
        
        assert file_obj.signatureType is None


class TestSmartAttributes:
    """Test SmartAttributes model."""
    
    def test_valid_smart_attributes(self):
        """Test creating a valid SmartAttributes."""
        attributes = SmartAttributes(
            patrolUuid="123e4567-e89b-12d3-a456-426614174000",
            patrolLegUuid="456e7890-e89b-12d3-a456-426614174000",
            patrolId="patrol-123",
            incidentId="incident-123",
            incidentUuid="789e0123-e89b-12d3-a456-426614174000",
            team="test-team",
            objective="test objective",
            comment="test comment",
            isArmed="false",
            transportType="vehicle",
            mandate="conservation",
            number=42,
            members=["member1", "member2"],
            leader="leader1",
            attachments=[
                File(filename="test.txt", data="data")
            ]
        )
        
        assert attributes.patrolUuid == "123e4567-e89b-12d3-a456-426614174000"
        assert attributes.patrolLegUuid == "456e7890-e89b-12d3-a456-426614174000"
        assert attributes.patrolId == "patrol-123"
        assert attributes.incidentId == "incident-123"
        assert attributes.incidentUuid == "789e0123-e89b-12d3-a456-426614174000"
        assert attributes.team == "test-team"
        assert attributes.objective == "test objective"
        assert attributes.comment == "test comment"
        assert attributes.isArmed == "false"
        assert attributes.transportType == "vehicle"
        assert attributes.mandate == "conservation"
        assert attributes.number == 42
        assert attributes.members == ["member1", "member2"]
        assert attributes.leader == "leader1"
        assert len(attributes.attachments) == 1
        assert attributes.attachments[0].filename == "test.txt"


class TestProperties:
    """Test Properties model."""
    
    def test_valid_properties(self):
        """Test creating a valid Properties."""
        properties = Properties(
            dateTime=datetime(2023, 1, 1, 10, 0, 0),
            smartDataType="incident",
            smartFeatureType="waypoint/new",
            smartAttributes=SmartAttributes(
                patrolUuid="123e4567-e89b-12d3-a456-426614174000"
            )
        )
        
        assert properties.dateTime == datetime(2023, 1, 1, 10, 0, 0)
        assert properties.smartDataType == "incident"
        assert properties.smartFeatureType == "waypoint/new"
        assert isinstance(properties.smartAttributes, SmartAttributes)
        assert properties.smartAttributes.patrolUuid == "123e4567-e89b-12d3-a456-426614174000"
    
    def test_properties_with_smart_observation(self):
        """Test Properties with SmartObservation."""
        properties = Properties(
            dateTime=datetime(2023, 1, 1, 10, 0, 0),
            smartDataType="observation",
            smartFeatureType="observation/new",
            smartAttributes=SmartObservation(
                category="test_category",
                attributes={}
            )
        )
        
        assert isinstance(properties.smartAttributes, SmartObservation)
        assert properties.smartAttributes.category == "test_category"


class TestSMARTRequest:
    """Test SMARTRequest model."""
    
    def test_valid_smart_request(self):
        """Test creating a valid SMARTRequest."""
        request = SMARTRequest(
            type="Feature",
            geometry=Geometry(coordinates=[123.45, -67.89]),
            properties=Properties(
                dateTime=datetime(2023, 1, 1, 10, 0, 0),
                smartDataType="incident",
                smartFeatureType="waypoint/new",
                smartAttributes=SmartAttributes(
                    patrolUuid="123e4567-e89b-12d3-a456-426614174000"
                )
            )
        )
        
        assert request.type == "Feature"
        assert request.geometry.coordinates == [123.45, -67.89]
        assert request.properties.smartDataType == "incident"
    
    def test_smart_request_json_serialization(self):
        """Test SMARTRequest JSON serialization."""
        request = SMARTRequest(
            type="Feature",
            geometry=Geometry(coordinates=[123.45, -67.89]),
            properties=Properties(
                dateTime=datetime(2023, 1, 1, 10, 0, 0),
                smartDataType="incident",
                smartFeatureType="waypoint/new",
                smartAttributes=SmartAttributes(
                    patrolUuid="123e4567-e89b-12d3-a456-426614174000"
                )
            )
        )
        
        json_str = request.json()
        data = json.loads(json_str)
        
        assert data["type"] == "Feature"
        assert data["geometry"]["coordinates"] == [123.45, -67.89]
        assert data["properties"]["smartDataType"] == "incident"
        assert data["properties"]["dateTime"] == "2023-01-01T10:00:00"


class TestSMARTResponse:
    """Test SMARTResponse model."""
    
    def test_valid_smart_response(self):
        """Test creating a valid SMARTResponse."""
        response = SMARTResponse(
            type="Feature",
            geometry=Geometry(coordinates=[123.45, -67.89]),
            properties=SMARTResponseProperties(
                fid="123e4567-e89b-12d3-a456-426614174000"
            )
        )
        
        assert response.type == "Feature"
        assert response.geometry.coordinates == [123.45, -67.89]
        assert response.properties.fid == "123e4567-e89b-12d3-a456-426614174000"


class TestPatrol:
    """Test Patrol model."""
    
    def test_valid_patrol(self):
        """Test creating a valid Patrol."""
        patrol = Patrol(
            armed=False,
            client_uuid="client-123",
            comment="Test patrol comment",
            conservation_area={"name": "Test CA"},
            end_date=date(2023, 1, 1),
            id="patrol-123",
            start_date=date(2023, 1, 1),
            uuid="123e4567-e89b-12d3-a456-426614174000"
        )
        
        assert patrol.uuid == "123e4567-e89b-12d3-a456-426614174000"
        assert patrol.id == "patrol-123"
        assert patrol.client_uuid == "client-123"
        assert patrol.comment == "Test patrol comment"
        assert patrol.armed is False
        assert patrol.start_date == date(2023, 1, 1)
        assert patrol.end_date == date(2023, 1, 1)


class TestPatrolDataModel:
    """Test PatrolDataModel model."""
    
    def test_valid_patrol_data_model(self):
        """Test creating a valid PatrolDataModel."""
        patrol_model = PatrolDataModel(
            patrolMetadata=[
                PatrolMetaData(
                    id="metadata-1",
                    names=[Names(name="Test Metadata", locale="en")],
                    type="test"
                )
            ]
        )
        
        assert len(patrol_model.patrolMetadata) == 1
        assert patrol_model.patrolMetadata[0].id == "metadata-1"
        assert patrol_model.patrolMetadata[0].type == "test"


class TestDataModel:
    """Test DataModel class."""
    
    def test_data_model_initialization(self):
        """Test DataModel initialization."""
        data_model = DataModel(use_language_code="en")

        data_model.load(open('tests/data/datamodel.xml').read())
        
        assert data_model.use_language_code == "en"
        assert hasattr(data_model, 'datamodel')
        assert hasattr(data_model, '_categories')
        assert hasattr(data_model, '_attributes')
    
    def test_data_model_load_method(self):
        """Test DataModel load method."""
        data_model = DataModel(use_language_code="en")
        
        # Test that load method exists (actual implementation would depend on the class)
        assert hasattr(data_model, 'load')
    

class TestConservationArea:
    """Test ConservationArea model."""
    
    def test_valid_conservation_area(self):
        """Test creating a valid ConservationArea."""
        ca = ConservationArea(
            label="Test Conservation Area",
            status="active",
            revision=1,
            uuid=uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
            description="A test conservation area"
        )
        
        assert ca.uuid == uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        assert ca.label == "Test Conservation Area"
        assert ca.description == "A test conservation area"
        assert ca.status == "active"
        assert ca.revision == 1


class TestConfigurableDataModel:
    """Test ConfigurableDataModel class."""
    
    def test_configurable_data_model_initialization(self):
        """Test ConfigurableDataModel initialization."""
        cdm = ConfigurableDataModel(
            cm_uuid="123e4567-e89b-12d3-a456-426614174000",
            use_language_code="en"
        )
        
        assert cdm.cm_uuid == "123e4567-e89b-12d3-a456-426614174000"
        assert cdm.use_language_code == "en"
    
    def test_configurable_data_model_methods(self):
        """Test ConfigurableDataModel methods."""
        cdm = ConfigurableDataModel(
            cm_uuid="123e4567-e89b-12d3-a456-426614174000",
            use_language_code="en"
        )
        
        # Test that required methods exist
        assert hasattr(cdm, 'load')
        assert hasattr(cdm, 'import_from_dict')
        assert hasattr(cdm, 'export_as_dict')


class TestSmartConnectApiInfo:
    """Test SmartConnectApiInfo model."""
    
    def test_api_info_with_minimal_data(self):
        """Test SmartConnectApiInfo with minimal data."""
        api_info = SmartConnectApiInfo.parse_obj({'build_version': "7.5"})
        
        assert api_info.build_version == "7.5"


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_conservation_area_serialization(self):
        """Test ConservationArea serialization."""
        ca = ConservationArea(
            label="Test CA",
            status="active",
            revision=1,
            uuid=uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
            description="Test Description"
        )
        
        # Test to dict
        ca_dict = ca.dict()
        assert ca_dict["uuid"] == uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        assert ca_dict["label"] == "Test CA"
        assert ca_dict["status"] == "active"
        
        # Test from dict
        ca_from_dict = ConservationArea.parse_obj(ca_dict)
        assert ca_from_dict.uuid == ca.uuid
        assert ca_from_dict.label == ca.label
    
    def test_patrol_serialization(self):
        """Test Patrol serialization."""
        patrol = Patrol(
            armed=False,
            client_uuid="client-123",
            comment="Test patrol comment",
            conservation_area={"name": "Test CA"},
            end_date=date(2023, 1, 1),
            id="patrol-123",
            start_date=date(2023, 1, 1),
            uuid="123e4567-e89b-12d3-a456-426614174000"
        )
        
        # Test to dict
        patrol_dict = patrol.dict()
        assert patrol_dict["uuid"] == "123e4567-e89b-12d3-a456-426614174000"
        assert patrol_dict["id"] == "patrol-123"
        assert patrol_dict["client_uuid"] == "client-123"
        
        # Test from dict
        patrol_from_dict = Patrol.parse_obj(patrol_dict)
        assert patrol_from_dict.uuid == patrol.uuid
        assert patrol_from_dict.id == patrol.id
    
    def test_smart_request_serialization(self):
        """Test SMARTRequest serialization."""
        request = SMARTRequest(
            type="Feature",
            geometry=Geometry(coordinates=[123.45, -67.89]),
            properties=Properties(
                dateTime=datetime(2023, 1, 1, 10, 0, 0),
                smartDataType="incident",
                smartFeatureType="waypoint/new",
                smartAttributes=SmartAttributes(
                    patrolUuid="123e4567-e89b-12d3-a456-426614174000"
                )
            )
        )
        
        # Test JSON serialization
        json_str = request.json()
        data = json.loads(json_str)
        
        assert data["type"] == "Feature"
        assert data["geometry"]["coordinates"] == [123.45, -67.89]
        assert data["properties"]["smartDataType"] == "incident"
        assert data["properties"]["dateTime"] == "2023-01-01T10:00:00"
