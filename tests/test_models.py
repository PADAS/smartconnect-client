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


MINIMAL_CM_XML_WITH_NODE_ID = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ConfigurableModel xmlns="http://www.smartconservationsoftware.org/xml/1.0/dataentry">
    <languages>
        <language code="en"/>
    </languages>
    <name language_code="en" value="Test Model"/>
    <nodes>
        <node id="abc-123" categoryKey="leaf-with-id" categoryHkey="root.leaf_with_id.">
            <name language_code="en" value="Leaf With ID"/>
        </node>
        <node categoryKey="leaf-no-id" categoryHkey="root.leaf_no_id.">
            <name language_code="en" value="Leaf No ID"/>
        </node>
    </nodes>
</ConfigurableModel>"""


class TestCategoryNodeId:
    """Test Category model's id field for CM node ids."""

    def test_category_model_accepts_optional_id(self):
        """Test that Category model accepts optional id field."""
        # Without id
        cat_without_id = Category(path="p", hkeyPath=None, display="D")
        assert cat_without_id.id is None

        # With id
        cat_with_id = Category(path="p", hkeyPath=None, display="D", id="x")
        assert cat_with_id.id == "x"

    def test_generate_node_paths_includes_node_id(self):
        """Test that generate_node_paths extracts and includes node id from CM XML."""
        cdm = ConfigurableDataModel(use_language_code="en", cm_uuid="cm-1")
        cdm.load(MINIMAL_CM_XML_WITH_NODE_ID)

        exported = cdm.export_as_dict()
        cats = exported["categories"]

        # Multiple categories emitted (one with id, one without).
        assert len(cats) == 2
        # The id-bearing node has its id populated.
        assert any(c.get("id") == "abc-123" for c in cats)
        # The id-less node yields id=None (safe-fallback path in _node_id).
        assert any(c.get("id") is None for c in cats)


MINIMAL_CM_XML_WITH_ATTRIBUTE_CONFIGS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ConfigurableModel xmlns="http://www.smartconservationsoftware.org/xml/1.0/dataentry">
    <languages>
        <language code="en"/>
    </languages>
    <name language_code="en" value="Test Model"/>
    <nodes>
        <node id="n1" categoryKey="cat1" categoryHkey="cat1.">
            <name language_code="en" value="Cat One"/>
            <attribute attributeKey="color" configId="cfg-color-default" type="LIST">
                <name language_code="en" value="Color"/>
                <option id="IS_VISIBLE" doubleValue="1.0"/>
            </attribute>
            <attribute attributeKey="notes" type="TEXT">
                <name language_code="en" value="Notes"/>
                <option id="IS_VISIBLE" doubleValue="1.0"/>
            </attribute>
        </node>
        <node id="n2" categoryKey="cat2" categoryHkey="cat2.">
            <name language_code="en" value="Cat Two"/>
            <attribute attributeKey="color" configId="cfg-color-custom" type="LIST">
                <name language_code="en" value="Color"/>
                <option id="IS_VISIBLE" doubleValue="1.0"/>
            </attribute>
        </node>
    </nodes>
    <attributeConfig id="cfg-color-default" attributeKey="color" isDefault="true">
        <name language_code="en" value="Color"/>
        <listItem keyRef="red" isActive="true"><name language_code="en" value="Red"/></listItem>
        <listItem keyRef="blue" isActive="false"><name language_code="en" value="Blue"/></listItem>
    </attributeConfig>
    <attributeConfig id="cfg-color-custom" attributeKey="color" isDefault="false">
        <name language_code="en" value="Color"/>
        <listItem keyRef="red" isActive="true"><name language_code="en" value="Red"/></listItem>
    </attributeConfig>
    <attributeConfig id="cfg-region" attributeKey="region" isDefault="true">
        <name language_code="en" value="Region"/>
        <treeNode keyRef="chobe" hkeyRef="chobe." isActive="true">
            <name language_code="en" value="Chobe"/>
            <children keyRef="mabele" hkeyRef="chobe.mabele." isActive="true">
                <name language_code="en" value="Mabele"/>
                <children keyRef="muchenje" hkeyRef="chobe.mabele.muchenje." isActive="true">
                    <name language_code="en" value="Muchenje"/>
                </children>
            </children>
            <children keyRef="kavimba" hkeyRef="chobe.kavimba." isActive="false">
                <name language_code="en" value="Kavimba"/>
                <children keyRef="kavimba1" hkeyRef="chobe.kavimba.kavimba1." isActive="true">
                    <name language_code="en" value="Kavimba 1"/>
                </children>
            </children>
        </treeNode>
        <treeNode keyRef="boteti" isActive="true">
            <name language_code="en" value="Boteti"/>
        </treeNode>
    </attributeConfig>
</ConfigurableModel>"""


def _load_cm_with_configs():
    cdm = ConfigurableDataModel(use_language_code="en", cm_uuid="cm-1")
    cdm.load(MINIMAL_CM_XML_WITH_ATTRIBUTE_CONFIGS)
    return cdm.export_as_dict()


class TestConfigurableModelConfigId:
    """attributeConfig identity is exposed so consumers can distinguish
    per-node curations of the same attribute key."""

    def test_generate_attributes_includes_config_id(self):
        attrs = _load_cm_with_configs()["attributes"]
        config_ids = [a.get("config_id") for a in attrs]
        assert config_ids == ["cfg-color-default", "cfg-color-custom", "cfg-region"]

    def test_generate_attributes_includes_is_default(self):
        attrs = _load_cm_with_configs()["attributes"]
        by_config = {a["config_id"]: a for a in attrs}
        assert by_config["cfg-color-default"]["is_default"] is True
        assert by_config["cfg-color-custom"]["is_default"] is False

    def test_duplicate_key_configs_both_present_in_document_order(self):
        """Two attributeConfigs for one attributeKey both survive, in
        document order — consumers that take the first entry per key keep
        today's behavior."""
        attrs = _load_cm_with_configs()["attributes"]
        color_entries = [a for a in attrs if a["key"] == "color"]
        assert [a["config_id"] for a in color_entries] == [
            "cfg-color-default",
            "cfg-color-custom",
        ]

    def test_node_attributes_include_config_id(self):
        cats = _load_cm_with_configs()["categories"]
        cat1 = next(c for c in cats if c["path"] == "cat1")
        cat2 = next(c for c in cats if c["path"] == "cat2")
        color1 = next(a for a in cat1["attributes"] if a["key"] == "color")
        color2 = next(a for a in cat2["attributes"] if a["key"] == "color")
        assert color1["config_id"] == "cfg-color-default"
        assert color2["config_id"] == "cfg-color-custom"

    def test_node_attribute_without_config_id_yields_none(self):
        cats = _load_cm_with_configs()["categories"]
        cat1 = next(c for c in cats if c["path"] == "cat1")
        notes = next(a for a in cat1["attributes"] if a["key"] == "notes")
        assert notes["config_id"] is None

    def test_export_import_round_trip_preserves_config_ids(self):
        cdm = ConfigurableDataModel(use_language_code="en", cm_uuid="cm-1")
        cdm.load(MINIMAL_CM_XML_WITH_ATTRIBUTE_CONFIGS)
        exported = cdm.export_as_dict()

        rehydrated = ConfigurableDataModel(use_language_code="en")
        rehydrated.import_from_dict(json.loads(json.dumps(exported)))
        assert rehydrated.export_as_dict()["attributes"] == exported["attributes"]

    def test_category_attribute_model_accepts_optional_config_id(self):
        assert CategoryAttribute(key="color").config_id is None
        assert (
            CategoryAttribute(key="color", config_id="cfg-1").config_id == "cfg-1"
        )


class TestGetListOptionsCM:
    """CM attributeConfig options: listItems stay flat; tree configs are
    recursed so CM-leaf nodes surface with dotted keys matching the base
    data model's TREE option keys (ERCS-8246)."""

    def test_name_child_is_skipped(self):
        """The <name> element must not leak into the options list."""
        attrs = _load_cm_with_configs()["attributes"]
        color = next(a for a in attrs if a.get("config_id") == "cfg-color-default")
        assert all(o["key"] for o in color["options"])

    def test_list_items_in_document_order(self):
        attrs = _load_cm_with_configs()["attributes"]
        color = next(a for a in attrs if a.get("config_id") == "cfg-color-default")
        assert color["options"] == [
            {"key": "red", "isActive": True},
            {"key": "blue", "isActive": False},
        ]

    def test_tree_config_yields_leaves_with_dotted_keys(self):
        """Only CM-leaf nodes surface, keyed by their dotted path — matching
        the base DM's TREE option keys so overlay matching works."""
        attrs = _load_cm_with_configs()["attributes"]
        region = next(a for a in attrs if a["key"] == "region")
        keys = [o["key"] for o in region["options"]]
        assert "chobe.mabele.muchenje" in keys
        # Parents with children are not options themselves.
        assert "chobe" not in keys
        assert "chobe.mabele" not in keys

    def test_tree_config_inactive_parent_cascades_to_leaves(self):
        """A leaf under a deactivated branch arrives inactive (effective
        is_active = own flag AND all ancestors')."""
        attrs = _load_cm_with_configs()["attributes"]
        region = next(a for a in attrs if a["key"] == "region")
        by_key = {o["key"]: o for o in region["options"]}
        # kavimba1 is active itself but its parent kavimba is inactive.
        assert by_key["chobe.kavimba.kavimba1"]["isActive"] is False
        assert by_key["chobe.mabele.muchenje"]["isActive"] is True

    def test_tree_node_without_children_is_its_own_leaf(self):
        """A childless treeNode without hkeyRef falls back to its keyRef."""
        attrs = _load_cm_with_configs()["attributes"]
        region = next(a for a in attrs if a["key"] == "region")
        by_key = {o["key"]: o for o in region["options"]}
        assert by_key["boteti"]["isActive"] is True


MINIMAL_DM_XML_WITH_TREE_AND_MLIST = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<DataModel xmlns="http://www.smartconservationsoftware.org/xml/1.1/datamodel">
    <languages>
        <languages code="en"/>
    </languages>
    <attributes>
        <attribute key="causeofdeath" isrequired="false" type="TREE">
            <names language_code="en" value="Cause of Death"/>
            <tree key="natural" isactive="true">
                <names language_code="en" value="Natural"/>
                <children key="disease" isactive="true">
                    <names language_code="en" value="Disease"/>
                </children>
                <children key="oldage" isactive="false">
                    <names language_code="en" value="Old Age"/>
                </children>
            </tree>
            <tree key="illegal" isactive="false">
                <names language_code="en" value="Illegal"/>
                <children key="poisoning" isactive="true">
                    <names language_code="en" value="Poisoning"/>
                </children>
            </tree>
        </attribute>
        <attribute key="actiontaken" isrequired="false" type="MLIST">
            <names language_code="en" value="Action Taken"/>
            <values key="warned" isactive="true">
                <names language_code="en" value="Warned"/>
            </values>
            <values key="arrested" isactive="false">
                <names language_code="en" value="Arrested"/>
            </values>
        </attribute>
    </attributes>
    <categories>
    </categories>
</DataModel>"""


def _load_dm_with_tree_and_mlist():
    dm = DataModel(use_language_code="en")
    dm.load(MINIMAL_DM_XML_WITH_TREE_AND_MLIST)
    return dm.export_as_dict()


class TestDataModelTreeOptions:
    """Base DM TREE options carry effective isActive (ERCS-8246: inactive
    SMART options were migrating as active because the parser dropped the
    flag for trees entirely)."""

    def test_tree_options_carry_is_active(self):
        attrs = _load_dm_with_tree_and_mlist()["attributes"]
        tree = next(a for a in attrs if a["key"] == "causeofdeath")
        by_key = {o["key"]: o for o in tree["options"]}
        assert by_key["natural"]["isActive"] is True
        assert by_key["natural.disease"]["isActive"] is True
        assert by_key["natural.oldage"]["isActive"] is False

    def test_tree_inactive_parent_cascades_to_children(self):
        attrs = _load_dm_with_tree_and_mlist()["attributes"]
        tree = next(a for a in attrs if a["key"] == "causeofdeath")
        by_key = {o["key"]: o for o in tree["options"]}
        assert by_key["illegal"]["isActive"] is False
        # poisoning is active itself but sits under the inactive branch.
        assert by_key["illegal.poisoning"]["isActive"] is False


class TestDataModelMlistOptions:
    """MLIST attributes parse their <values> options exactly like LIST
    (previously they came out with options=None)."""

    def test_mlist_options_parsed(self):
        attrs = _load_dm_with_tree_and_mlist()["attributes"]
        mlist = next(a for a in attrs if a["key"] == "actiontaken")
        assert mlist["options"] == [
            {"key": "warned", "isActive": True, "display": "Warned"},
            {"key": "arrested", "isActive": False, "display": "Arrested"},
        ]
