import pytest
from ckan.tests import factories
from ckan.logic import ValidationError
from ckan.tests.helpers import call_action


@pytest.mark.ckan_config("ckan.plugins", "fjelltopp_security")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestSecureGroupActions:

    def test_group_create_with_valid_data(self, context):

        group_dict = {
            'name': 'testgroup',
            'title': 'Test Group',
            'image_url': '/images/test-group-image.jpg'
        }
        group = call_action('group_create', context=context, **group_dict)
        assert group['image_url'] == group_dict['image_url']


    @pytest.mark.parametrize("image_url", [
        'http://example.com/group-image.jpg',
        'https://example.com/group-image.jpg',
        '//example.com/group-image.jpg'
    ])
    def test_group_create_with_external_image_fails(self, image_url, context):
        with pytest.raises(ValidationError) as exception_info:
            call_action(
                'group_create',
                name='testgroup',
                title='Test Group',
                image_url=image_url,
                context=context
            )


    def test_group_create_without_image_url(self, context):
        group = call_action(
            'group_create',
            context=context,
            name='testgroup',
            title='Test Group',
            image_url=None
        )
        assert 'image_url' not in group or not group['image_url']


    def test_group_update_with_valid_data(self, group):
        update_dict = {
            'id': group['id'],
            'name': group['name'],
            'title': 'Updated Test Group',
            'image_url': '/images/updated-group-image.jpg',
        }
        updated_group = call_action('group_update', **update_dict)
        assert updated_group['image_url'] == update_dict['image_url']


    def test_group_update_without_image_url(self, group):
        original_image_url = group['image_url']
        update_dict = {
            'id': group['id'],
            'name': group['name'],
            'title': 'Updated Test Group'
        }
        updated_group = call_action('group_update', **update_dict)
        assert updated_group['image_url'] == original_image_url


    @pytest.mark.parametrize("image_url", [
        'http://example.com/group-image.jpg',
        'https://example.com/group-image.jpg',
        '//example.com/group-image.jpg'
    ])
    def test_group_update_with_external_image_fails(self, group, image_url):
        with pytest.raises(ValidationError) as exception_info:
            call_action(
                'group_update',
                id=group['id'],
                name=group['name'],
                title='Updated Test Group',
                image_url=image_url
            )

