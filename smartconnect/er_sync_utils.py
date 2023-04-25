import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import UUID

import pydantic
from cdip_connector.core.schemas import ERSubject
from pydantic import BaseModel, parse_obj_as, Field

from smartconnect import PatrolDataModel, cache
from smartconnect.models import Category, Attribute, CategoryAttribute

logger = logging.getLogger(__name__)

smart_er_type_mapping = {'TEXT': 'string',
                         'NUMERIC': 'number',
                         'BOOLEAN': 'boolean',
                         'TREE': 'array',
                         'LIST': 'array',
                         'DATE': 'string'}

class EventSchema(BaseModel):
    type: str = 'object'
    json_schema: str = Field(alias="$schema", default='http://json-schema.org/draft-04/schema#')
    properties: Optional[dict]
    definition: Optional[List]


class SchemaWrapper(BaseModel):
    schema_wrapper: EventSchema = Field(alias="schema")


class EREventType(BaseModel):
    id: Optional[UUID]
    category: Optional[str]
    value: str
    display: str
    event_schema: Optional[str] = Field(alias="schema")
    is_active: bool = True


class EarthRangerReaderState(pydantic.BaseModel):
    event_last_poll_at: Optional[datetime] = datetime.now(tz=timezone.utc) - timedelta(
        days=7
    )
    patrol_last_poll_at: Optional[datetime] = datetime.now(tz=timezone.utc) - timedelta(
        days=7
    )


def is_leaf_node(*, node_paths, cur_node):
    is_leaf = True
    for path in node_paths:
        # determine if current path is subset of any category path
        if cur_node in path and len(path) > len(cur_node) and '.' in path:
            is_leaf = False
            break
    return is_leaf


def build_earth_ranger_event_types(*, dm: dict, ca_uuid: str, ca_identifier: str, cdm: dict = None):
    """Builds Earth Ranger Event Types from SMART CA data model or configurable data model if provided"""
    cats = parse_obj_as(List[Category], cdm.get('categories')) if cdm else parse_obj_as(List[Category], dm.get('categories'))
    cat_paths = [cat.path for cat in cats]
    attributes = parse_obj_as(List[Attribute], dm.get('attributes'))
    attributeConfigs = cdm.get('attributes') if cdm else None
    er_event_types = []

    for cat in cats:
        try:
            leaf_attributes = cat.attributes
            is_multiple = cat.is_multiple
            is_active = cat.is_active and is_leaf_node(node_paths=cat_paths, cur_node=cat.path) if not cdm else True
            path_components = str.split(cat.hkeyPath, sep='.') if cdm else str.split(cat.path, sep='.')
            value = '_'.join(path_components)
            # appending ca_uuid prefix to avoid collision on equivalent cat paths in different CA's
            value = f'{ca_uuid}_{value}'
            display = f'{ca_identifier} - {cat.display}'
            if not cdm:
                # Add inherited attributes for regular DataModel Flow
                inherited_attributes = get_inherited_attributes(cats, path_components)
                leaf_attributes.extend(inherited_attributes)


            er_event_type = EREventType(value=value,
                                        display=display,
                                        is_active=is_active)

            if is_active:
                if not leaf_attributes:
                    logger.warning(f'Skipping event type, no leaf attributes detected', extra=dict(value=value,
                                                                                                   display=display))
                    # Dont create event_types for leaves with no attributes
                    continue

                schema = build_schema_and_form_definition(attributes=attributes, leaf_attributes=leaf_attributes,
                                                          is_multiple=is_multiple, attributeConfigs=attributeConfigs)

                if not schema.properties:
                    logger.warning(f'Skipping event type, no schema properties detected',
                                   extra=dict(event_type=er_event_type))
                    # ER wont create event with no schema properties
                    continue

                # ER API requires schema as a string
                er_event_type.event_schema = json.dumps(SchemaWrapper(schema=schema).dict(by_alias=True), indent=2)

            er_event_types.append(er_event_type)
        except Exception as e:
            logger.error(f"Exception occured building ER event type from SMART category {cat}")
            raise e
    return er_event_types


def get_inherited_attributes(cats: List[Category], path_components: list):
    inherited_attributes = []
    parent_cat_path = ''
    # iterate through parent paths associated to current leaf and look up the category to get its attributes
    for component in path_components[:-1]:  # skip last path component as that is current leaf
        if parent_cat_path == '':  # root parent category
            parent_cat_path = component
        else:
            parent_cat_path = f'{parent_cat_path}.{component}'
        parent_cat = next((x for x in cats if x.path == parent_cat_path), None)
        if parent_cat:
            parent_attributes: list = parent_cat.attributes
            inherited_attributes.extend(parent_attributes)
    return inherited_attributes


def get_leaf_options(options):
    leaf_options = []
    option_keys = [option.key for option in options]
    for option in options:
        if is_leaf_node(node_paths=option_keys, cur_node=option.key):
            leaf_options.append(option)
    return leaf_options


def get_leaf_options_with_config(options, optionsConfig = None):
    leaf_options = []
    for optionConfig in optionsConfig:
        if optionConfig.get('key') is not None:
            isActive = optionConfig.get('isActive')
            option = next((option for option in options if optionConfig.get('key') == option.key), None)
            if not option:
                logger.warning(f"No option found for config {optionConfig.get('key')}")
            if isActive and option:
                leaf_options.append(option)
    return leaf_options


def build_schema_and_form_definition(*, attributes: List[Attribute], leaf_attributes: List[CategoryAttribute], is_multiple: bool, attributeConfigs = None):
    properties = {}
    schema_definition = []
    attribute_meta: CategoryAttribute
    for attribute_meta in leaf_attributes:
        try:
            key = attribute_meta.key
            is_active = attribute_meta.is_active
            attribute = next((x for x in attributes if x.key == key), None)
            attributeOptionsConfig = next((config['options'] for config in attributeConfigs if config['key'] == key), None) if attributeConfigs else None
            if attribute:
                if not is_active:
                    # TODO: Find out from ER core why exclusion from schema definition not hiding field in report
                    #  Excluding entirely form schema for now if not is_active until that ability is determined
                    continue
                schema_definition.append(key)
                # Right now we are not supporting multiple observation support
                if is_multiple and False:
                    # create event type that allows multiple value entries
                    type = attribute.type
                    converted_type = smart_er_type_mapping[type]
                    display = attribute.display
                    properties[key] = dict(type=converted_type,
                                           title=display)
                    options = attribute.options
                    if options:
                        if attributeOptionsConfig:
                            options = get_leaf_options_with_config(options, optionsConfig=attributeOptionsConfig)
                        else:
                            options = get_leaf_options(options)
                        option_values = [dict(title=x.display, const=x.key) for x in options]
                        properties[key]['items'] = dict(type='string',
                                                        oneOf=option_values)
                else:
                    # create event type that allows single value entry
                    display = attribute.display
                    converted_type = smart_er_type_mapping[attribute.type]
                    converted_type = converted_type if converted_type is not 'array' else 'string'
                    properties[key] = dict(type=converted_type,
                                           title=display)
                    options = attribute.options
                    if options:
                        if attributeOptionsConfig:
                            options = get_leaf_options_with_config(options, optionsConfig=attributeOptionsConfig)
                        else:
                            options = get_leaf_options(options)
                        enum_values = [x.key for x in options]
                        enum_display = [x.display for x in options]
                        properties[key]['enum'] = enum_values
                        properties[key]['enumNames'] = enum_display
            else:
                print('Failed to find attribute')
        except Exception as e:
            logger.error(f"Error occurred while building schema for category attribute key {key}")
    # append_custom_attributes(properties=properties)
    schema = EventSchema(definition=schema_definition,
                         properties=properties,
                         type='object')
    return schema


def append_custom_attributes(properties):
    """ Was using this to append custom attributes like SMART Observation UUID """
    key = 'smart_observation_uuid'
    properties[key] = dict(type='string',
                           title='SMART Observation UUID')


def er_event_type_schemas_equal(schema1: dict, schema2: dict):
    return schema1.get('properties') == schema2.get('properties') and schema1.get('definition') == schema2.get('definition')


def er_subjects_equal(subject1: ERSubject, subject2: ERSubject):
    #Todo: revisit this, to see whether IDs are appropriate. Or add a side-data identifier for the subjects added by this routine.
    return subject1.name == subject2.name


def get_subjects_from_patrol_data_model(pm: PatrolDataModel, ca_uuid: str):
    # create ER subjects from Patrol Data Model members
    members = next((metaData for metaData in pm.patrolMetadata if metaData.id == "members"), None)
    subjects = []
    if members:
        for member in members.listOptions:
            if member.names:
                subject = ERSubject(name=member.names[0].name,
                                    subject_subtype='ranger',
                                    additional=dict(smart_member_id=member.id,
                                                    ca_uuid=ca_uuid),
                                    is_active=True)
                subjects.append(subject)
    return subjects


def get_earth_ranger_last_poll(integration_id: str):
    er_state = EarthRangerReaderState.parse_obj(cache.get_state(integration_id=integration_id))
    return er_state


def set_earth_ranger_last_poll(integration_id: str, state: EarthRangerReaderState):
    cache.save_poll_time(state=state.json(), integration_id=integration_id)




