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
                'image_url': ['Image URL must be a local path. External URLs are not allowed']
            })


@toolkit.chained_action
def validate_image_url_first(original_action, context, data_dict):
    """
    Checks the data dict for an image_url, and ensures it is a valid upload.
    """
    validate_no_external_images(data_dict)
    return original_action(context, data_dict)
