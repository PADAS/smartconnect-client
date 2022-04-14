import json
import logging

from cdip_connector.core.schemas import ERSubject

from smartconnect import PatrolDataModel

logger = logging.getLogger(__name__)

smart_er_type_mapping = {'TEXT': 'string',
                         'NUMERIC': 'number',
                         'BOOLEAN': 'boolean',
                         'TREE': 'array',
                         'LIST': 'array'}


def build_earth_ranger_event_types(dm: dict):
    """Builds Earth Ranger Event Types from SMART CA data model"""
    # TODO: create pydantic models for flow below
    cats = dm.get('categories')
    attributes = dm.get('attributes')
    er_event_types = []

    for cat in cats:
        path = cat.get('path')
        leaf_attributes: list = cat.get('attributes')
        isMultiple = cat.get('ismultiple') == 'true'
        path_components = str.split(path, sep='.')
        value = '_'.join(path_components)
        display = ' '.join([s.capitalize() for s in path_components])
        er_event_type = dict(value=value,
                             display=display)
        inherited_attributes = get_inherited_attributes(cats, path_components)
        leaf_attributes.extend(inherited_attributes)
        if not leaf_attributes:
            # Dont create event_types for leaves with no attributes
            continue

        schema = build_schema_and_form_definition(attributes=attributes, leaf_attributes=leaf_attributes,
                                                  isMultiple=isMultiple)

        # ER API requires schema as a string
        er_event_type['schema'] = json.dumps(dict(schema=schema))
        er_event_types.append(er_event_type)
    return er_event_types


def get_inherited_attributes(cats: list, path_components: list):
    inherited_attributes = []
    parent_cat_path = ''
    # iterate through parent paths associated to current leaf and look up the category to get its attributes
    for component in path_components[:-1]:  # skip last path component as that is current leaf
        if parent_cat_path == '':  # root parent category
            parent_cat_path = component
        else:
            parent_cat_path = f'{parent_cat_path}.{component}'
        parent_cat = next((x for x in cats if x.get('path') == parent_cat_path), None)
        if parent_cat:
            parent_attributes: list = parent_cat.get('attributes')
            inherited_attributes.extend(parent_attributes)
    return inherited_attributes


def build_schema_and_form_definition(*, attributes: list, leaf_attributes: list, isMultiple: bool):
    schema = dict(type='object',
                  properties={})
    schema['$schema'] = 'http://json-schema.org/draft-04/schema#'
    schema_definition = []
    for attribute_meta in leaf_attributes:
        key = attribute_meta.get('key')
        isactive = attribute_meta.get('isactive')
        attribute = next((x for x in attributes if x.get('key') == key), None)
        if attribute:
            if isactive:
                # TODO: Find out from ER core why exclusion from schema definition not hiding field in report
                schema_definition.append(key)
            if isMultiple:
                # create event type that allows multiple value entries
                type = attribute.get('type')
                converted_type = smart_er_type_mapping[type]
                display = attribute.get('display')
                schema['properties'][key] = dict(type=converted_type,
                                                 title=display)
                options = attribute.get('options')
                if options:
                    option_values = [dict(title=x.get('display'), const=x.get('key')) for x in options]
                    schema['properties'][key]['items'] = dict(type='string',
                                                              oneOf=option_values)
            else:
                # create event type that allows single value entry
                display = attribute.get('display')
                schema['properties'][key] = dict(type='string',
                                                 title=display)
                options = attribute.get('options')
                if options:
                    enum_values = [x.get('key') for x in options]
                    enum_display = [x.get('display') for x in options]
                    schema['properties'][key]['enum'] = enum_values
                    schema['properties'][key]['enumNames'] = enum_display
        else:
            print('Failed to find attribute')
    schema['definition'] = schema_definition
    return schema


def er_event_type_schemas_equal(schema1: dict, schema2: dict):
    return schema1.get('properties') == schema2.get('properties') and schema1.get('definition') == schema2.get('definition')


def er_subjects_equal(subject1: ERSubject, subject2: ERSubject):
    return subject1.name == subject2.name


def get_subjects_from_patrol_data_model(pm: PatrolDataModel):
    # create ER subjects from Patrol Data Model members
    members = next((metaData for metaData in pm.patrolMetadata if metaData.id == "members"), None)
    subjects = []
    if members:
        for member in members.listOptions:
            if member.names:
                subject = ERSubject(name=member.names[0].name,
                                    subject_subtype='ranger',
                                    additional=dict(smart_member_id=member.id),
                                    is_active=True)
                subjects.append(subject)
    return subjects




