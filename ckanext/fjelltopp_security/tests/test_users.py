import pytest
from ckan.logic import ValidationError
from ckan.tests.helpers import call_action


@pytest.mark.ckan_config("ckan.plugins", "fjelltopp_security")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestSecureUserActions:

    def test_user_create_with_valid_data(self, context):
        """Test user creation with valid local image URL succeeds."""
        user_dict = {
            'name': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePassword123',
            'image_url': '/images/test-image.jpg'
        }
        created_user = call_action('user_create', context=context, **user_dict)
        assert created_user['image_url'] == user_dict['image_url']


    @pytest.mark.parametrize("image_url", [
        'http://example.com/image.jpg',
        'https://example.com/image.jpg',
        '//example.com/image.jpg'
    ])
    def test_user_create_with_external_image_fails(self, context, image_url):
        user_dict = {
            'name': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePassword123',
            'image_url': 'https://example.com/image.jpg'
        }
        with pytest.raises(ValidationError):
            call_action('user_create', context=context, **user_dict)


    def test_user_create_without_image_url(self, context):
        user_dict = {
            'name': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePassword123'
        }
        created_user = call_action('user_create', context=context, **user_dict)
        assert 'image_url' not in created_user or not created_user['image_url']


    def test_user_update_with_valid_data(self, context):
        update_dict = {
            'id': context['id'],
            'email': 'test@example.com',
            'image_url': '/images/updated-image.jpg'
        }
        updated_user = call_action('user_update', context=context, **update_dict)
        assert updated_user['image_url'] == update_dict['image_url']

    @pytest.mark.parametrize("image_url", [
        'http://example.com/image.jpg',
        'https://example.com/image.jpg',
        '//example.com/image.jpg'
    ])
    def test_user_update_with_external_data(self, context, image_url):
        update_dict = {
            'id': context['id'],
            'email': 'test@example.com',
            'image_url': 'https://example.com/image.jpg'
        }
        with pytest.raises(ValidationError):
            call_action('user_update', context=context, **update_dict)


    def test_user_update_without_image_url(self, user, context):
        original_image_url = user['image_url']
        update_dict = {
            'id': context['id'],
            'email': 'test@example.com'
        }
        updated_user = call_action('user_update', context=context, **update_dict)
        assert updated_user['image_url'] == original_image_url
