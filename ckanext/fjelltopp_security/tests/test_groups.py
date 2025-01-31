import pytest
from ckan.tests import factories
from ckan.plugins import toolkit
from ckan.logic import ValidationError


@pytest.mark.ckan_config("ckan.plugins", "fjelltopp_security")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestSecureGroupActions:

    @pytest.fixture
    def base_group(self):
        """Create a basic group with factories."""
        return factories.Group(
            image_url='/images/test-group-image.jpg'
        )

    def test_group_create_with_valid_data(self):
        """Test group creation with valid local image URL succeeds."""
        group_dict = {
            'name': 'testgroup',
            'title': 'Test Group',
            'image_url': '/images/test-group-image.jpg'
        }
        group = factories.Group(**group_dict)

        assert group['name'] == group_dict['name']
        assert group['title'] == group_dict['title']
        assert group['image_url'] == group_dict['image_url']

    @pytest.mark.parametrize("image_url", [
        'http://example.com/group-image.jpg',
        'https://example.com/group-image.jpg',
        '//example.com/group-image.jpg'
    ])
    def test_group_create_with_external_image_fails(self, image_url):
        """Test group creation fails with external image URLs."""
        with pytest.raises(ValidationError) as exception_info:
            factories.Group(
                image_url=image_url
            )

        assert 'Image URL must be a local path. External URLs are not allowed' in str(exception_info.value)

    def test_group_create_without_image_url(self):
        """Test group creation succeeds without an image URL."""
        group = factories.Group(image_url=None)
        assert 'image_url' not in group or not group['image_url']

    def test_group_update_with_valid_data(self, base_group):
        """Test group update with valid local image URL succeeds."""
        update_dict = {
            'id': base_group['id'],
            'name': 'testgroup',
            'title': 'Updated Test Group',
            'image_url': '/images/updated-group-image.jpg'
        }
        updated_group = toolkit.get_action('group_update')(
            context={'ignore_auth': True},
            data_dict=update_dict
        )
        assert updated_group['image_url'] == update_dict['image_url']
        assert updated_group['title'] == update_dict['title']

    def test_group_update_without_image_url(self, base_group):
        """Test group update succeeds when not modifying image URL."""
        original_image_url = base_group['image_url']
        update_dict = {
            'id': base_group['id'],
            'name': 'testgroup',
            'title': 'Updated Test Group'
        }
        updated_group = toolkit.get_action('group_update')(
            context={'ignore_auth': True},
            data_dict=update_dict
        )
        assert updated_group['image_url'] == original_image_url

    @pytest.mark.parametrize("image_url", [
        'http://example.com/group-image.jpg',
        'https://example.com/group-image.jpg',
        '//example.com/group-image.jpg'
    ])
    def test_group_update_with_external_image_fails(self, base_group, image_url):
        """Test group update fails with external image URLs."""
        update_dict = {
            'id': base_group['id'],
            'name': 'testgroup',
            'title': 'Updated Test Group',
            'image_url': image_url
        }
        with pytest.raises(ValidationError) as exception_info:
            toolkit.get_action('group_update')(
                context={'ignore_auth': True},
                data_dict=update_dict
            )

        assert 'Image URL must be a local path. External URLs are not allowed' in str(exception_info.value)
