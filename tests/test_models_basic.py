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
    ConservationArea,
    SmartConnectApiInfo
)


class TestBasicModels:
    """Test basic model functionality that works."""
    
    def test_category_attribute_basic(self):
        """Test basic CategoryAttribute creation."""
        attr = CategoryAttribute(key="test_key")
        assert attr.key == "test_key"
        assert attr.is_active is True
    
    def test_attribute_option_basic(self):
        """Test basic AttributeOption creation."""
        option = AttributeOption(key="option1", display="Option 1")
        assert option.key == "option1"
        assert option.display == "Option 1"
        assert option.is_active is True
    
    def test_attribute_basic(self):
        """Test basic Attribute creation."""
        attr = Attribute(
            key="test_attr",
            type="string",
            display="Test Attribute"
        )
        assert attr.key == "test_attr"
        assert attr.type == "string"
        assert attr.display == "Test Attribute"
        assert attr.isrequired is False
    
    def test_transformation_rule_basic(self):
        """Test basic TransformationRule creation."""
        rule = TransformationRule(
            match_pattern={"field": "value"},
            transforms={"field": "new_value"}
        )
        assert rule.match_pattern == {"field": "value"}
        assert rule.transforms == {"field": "new_value"}
    
    def test_smart_observation_basic(self):
        """Test basic SmartObservation creation."""
        observation = SmartObservation(
            category="test_category",
            attributes={"key": "value"}
        )
        assert observation.category == "test_category"
        assert observation.attributes == {"key": "value"}
        assert observation.observationUuid is None
    
    def test_smart_observation_group_basic(self):
        """Test basic SmartObservationGroup creation."""
        group = SmartObservationGroup(
            observations=[
                SmartObservation(
                    category="test_category",
                    attributes={}
                )
            ]
        )
        assert len(group.observations) == 1
        assert group.observations[0].category == "test_category"
    
    def test_geometry_basic(self):
        """Test basic Geometry creation."""
        geometry = Geometry(coordinates=[123.45, -67.89])
        assert geometry.coordinates == [123.45, -67.89]
    
    def test_geometry_validation_too_few_coordinates(self):
        """Test Geometry validation with too few coordinates."""
        with pytest.raises(ValidationError):
            Geometry(coordinates=[123.45])
    
    def test_file_basic(self):
        """Test basic File creation."""
        file_obj = File(
            filename="test.txt",
            data="base64_encoded_data"
        )
        assert file_obj.filename == "test.txt"
        assert file_obj.data == "base64_encoded_data"
        assert file_obj.signatureType is None
    
    def test_smart_attributes_basic(self):
        """Test basic SmartAttributes creation."""
        attributes = SmartAttributes(
            patrolUuid="123e4567-e89b-12d3-a456-426614174000",
            patrolLegUuid="456e7890-e89b-12d3-a456-426614174000"
        )
        assert attributes.patrolUuid == "123e4567-e89b-12d3-a456-426614174000"
        assert attributes.patrolLegUuid == "456e7890-e89b-12d3-a456-426614174000"
    
    def test_properties_basic(self):
        """Test basic Properties creation."""
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
    
    def test_smart_request_basic(self):
        """Test basic SMARTRequest creation."""
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
    
    def test_conservation_area_basic(self):
        """Test basic ConservationArea creation."""
        ca = ConservationArea(
            label="Test CA",
            status="active",
            revision=1,
            uuid=uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        )
        assert ca.label == "Test CA"
        assert ca.status == "active"
        assert ca.revision == 1
        assert ca.uuid == uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
    
    def test_smart_connect_api_info_basic(self):
        """Test basic SmartConnectApiInfo creation."""
        # Test with alias names (the way it's actually used)
        api_info = SmartConnectApiInfo(
            **{
                "build-date": "2023-01-01",
                "build-version": "1.0.0",
                "db-last-updated": "2023-01-01T10:00:00"
            }
        )
        assert api_info.build_date == "2023-01-01"
        assert api_info.build_version == "1.0.0"
        assert api_info.db_last_updated == "2023-01-01T10:00:00"


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_category_attribute_serialization(self):
        """Test CategoryAttribute serialization."""
        attr = CategoryAttribute(key="test_key", is_active=True)
        
        # Test to dict
        attr_dict = attr.dict()
        assert attr_dict["key"] == "test_key"
        assert attr_dict["is_active"] is True
        
        # Test from dict
        attr_from_dict = CategoryAttribute.parse_obj(attr_dict)
        assert attr_from_dict.key == attr.key
        assert attr_from_dict.is_active == attr.is_active
    
    def test_geometry_serialization(self):
        """Test Geometry serialization."""
        geometry = Geometry(coordinates=[123.45, -67.89])
        
        # Test to dict
        geom_dict = geometry.dict()
        assert geom_dict["coordinates"] == [123.45, -67.89]
        
        # Test from dict
        geom_from_dict = Geometry.parse_obj(geom_dict)
        assert geom_from_dict.coordinates == geometry.coordinates
    
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
        
        # Test JSON serialization
        json_str = request.json()
        data = json.loads(json_str)
        
        assert data["type"] == "Feature"
        assert data["geometry"]["coordinates"] == [123.45, -67.89]
        assert data["properties"]["smartDataType"] == "incident"
        assert data["properties"]["dateTime"] == "2023-01-01T10:00:00"
    
    def test_conservation_area_serialization(self):
        """Test ConservationArea serialization."""
        ca = ConservationArea(
            label="Test CA",
            status="active",
            revision=1,
            uuid=uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        )
        
        # Test to dict
        ca_dict = ca.dict()
        assert ca_dict["label"] == "Test CA"
        assert ca_dict["status"] == "active"
        assert ca_dict["uuid"] == uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        
        # Test from dict
        ca_from_dict = ConservationArea.parse_obj(ca_dict)
        assert ca_from_dict.label == ca.label
        assert ca_from_dict.uuid == ca.uuid


class TestModelValidation:
    """Test model validation."""
    
    def test_geometry_validation(self):
        """Test Geometry validation."""
        # Valid geometry
        geometry = Geometry(coordinates=[123.45, -67.89])
        assert geometry.coordinates == [123.45, -67.89]
        
        # Invalid geometry - too few coordinates
        with pytest.raises(ValidationError):
            Geometry(coordinates=[123.45])
    
    def test_smart_observation_validation(self):
        """Test SmartObservation validation."""
        # Valid observation
        observation = SmartObservation(
            category="test_category",
            attributes={"key": "value"}
        )
        assert observation.category == "test_category"
        assert observation.attributes == {"key": "value"}
        
        # Test with None UUID
        observation_none = SmartObservation.parse_raw(json.dumps(dict(
            observationUuid="None",
            category="test_category",
            attributes={},
        )))

        assert observation_none.observationUuid == None  # String "None", not None
    
    def test_conservation_area_validation(self):
        """Test ConservationArea validation."""
        # Valid conservation area
        ca = ConservationArea(
            label="Test CA",
            status="active",
            revision=1,
            uuid=uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        )
        assert ca.label == "Test CA"
        assert ca.status == "active"
        
        # Missing required fields should raise validation error
        with pytest.raises(ValidationError):
            ConservationArea(
                label="Test CA"
                # Missing status, revision, uuid
            )
