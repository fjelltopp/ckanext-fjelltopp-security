import ckan.plugins.toolkit as toolkit
from ckan.logic.action.update import (
    user_update as core_user_update,
    group_update as core_group_update,
    organization_update as core_organization_update
)
from ckan.logic.action.create import (
    user_create as core_user_create,
    group_create as core_group_create,
    organization_create as core_organization_create
)


def validate_no_external_images(data_dict):
    """
    Validate that no external image URLs are used.
    Raises ValidationError if an external URL is found.
    """
    if 'image_url' in data_dict and data_dict['image_url']:
        image_url = data_dict['image_url'].strip()
        if image_url and image_url.startswith(('http://', 'https://', '//')):
            raise toolkit.ValidationError({
                'image_url': ['External image URLs are not allowed for security reasons']
            })


def secure_user_update(context, data_dict):
    """
    Custom user update action that extends CKAN's default user_update.
    """
    validate_no_external_images(data_dict)
    return core_user_update(context, data_dict)


def secure_user_create(context, data_dict):
    """
    Custom user create action that extends CKAN's default user_create.
    """
    validate_no_external_images(data_dict)
    return core_user_create(context, data_dict)


def secure_group_update(context, data_dict):
    """
    Custom group update action that extends CKAN's default group_update.
    Validates that no external images are used in the group.
    """
    validate_no_external_images(data_dict)
    return core_group_update(context, data_dict)


def secure_group_create(context, data_dict):
    """
    Custom group create action that extends CKAN's default group_create.
    Validates that no external images are used in the group.
    """
    validate_no_external_images(data_dict)
    return core_group_create(context, data_dict)


def secure_organization_update(context, data_dict):
    """
    Custom organization update action that extends CKAN's default organization_update.
    Validates that no external images are used in the organization.
    """
    validate_no_external_images(data_dict)
    return core_organization_update(context, data_dict)


def secure_organization_create(context, data_dict):
    """
    Custom organization create action that extends CKAN's default organization_create.
    Validates that no external images are used in the organization.
    """
    validate_no_external_images(data_dict)
    return core_organization_create(context, data_dict)
