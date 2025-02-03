import pytest
from ckan.tests import factories
from ckan.plugins import toolkit
from ckan.logic import ValidationError


@pytest.mark.ckan_config("ckan.plugins", "fjelltopp_security")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestSecureUserActions:

    @pytest.fixture
    def base_user(self):
        """Create a basic user with factories."""
        return factories.User(
            image_url='/images/test-image.jpg'
        )


    def test_user_create_with_valid_data(self):
        """Test user creation with valid local image URL succeeds."""
        user_dict = {
            'name': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePassword123',
            'image_url': '/images/test-image.jpg'
        }
        user = factories.User(**user_dict)
        assert user['name'] == user_dict['name']
        assert user['email'] == user_dict['email']
        assert user['image_url'] == user_dict['image_url']


    @pytest.mark.parametrize("image_url", [
        'http://example.com/image.jpg',
        'https://example.com/image.jpg',
        '//example.com/image.jpg'
    ])
    def test_user_create_with_external_image_fails(self, image_url):
        """Test user creation fails with external image URLs."""
        with pytest.raises(ValidationError) as exception_info:
            factories.User(
                image_url=image_url
            )
        assert 'Image URL must be a local path. External URLs are not allowed' in str(exception_info.value)


    def test_user_create_without_image_url(self):
        """Test user creation succeeds without an image URL."""
        user = factories.User(image_url=None)
        assert 'image_url' not in user or not user['image_url']


    def test_user_update_with_valid_data(self, base_user):
        """Test user update with valid local image URL succeeds."""
        update_dict = {
            'id': base_user['id'],
            'email': 'test@example.com',
            'image_url': '/images/updated-image.jpg'
        }
        updated_user = toolkit.get_action('user_update')(
            context={'ignore_auth': True},
            data_dict=update_dict
        )
        assert updated_user['image_url'] == update_dict['image_url']


    def test_user_update_without_image_url(self, base_user):
        """Test user update succeeds when not modifying image URL."""
        original_image_url = base_user['image_url']
        update_dict = {
            'id': base_user['id'],
            'email': 'test@example.com'
        }
        updated_user = toolkit.get_action('user_update')(
            context={'ignore_auth': True},
            data_dict=update_dict
        )
        assert updated_user['image_url'] == original_image_url

    # WEB API
    @pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
    class TestSecureUserAPI:

        def test_api_user_create_with_external_image(self, _call_api, _assert):
            """Test that the API blocks external images during user creation."""
            user_dict = {
                'name': 'apitestuser',
                'email': 'apitest@example.com',
                'password': 'APITestPass123',
                'image_url': 'https://example.com/image.jpg'
            }
            _assert(
                _call_api(user_dict, 'user_create', True),
                False
            )


        def test_api_user_create_with_valid_image(self, _call_api, _assert):
            """Test that the API allows local image paths during user creation."""
            user_dict = {
                'name': 'apitestuser',
                'email': 'apitest@example.com',
                'password': 'APITestPass123',
                'image_url': '/images/test-image.jpg'
            }
            _assert(
                _call_api(user_dict, 'user_create'),
                True
            )


        def test_api_user_update_with_external_image(self, _call_api, _assert):
            """Test that the API blocks external images during user update."""
            user = factories.User(
                image_url='/images/default-user.png'
            )
            update_dict = {
                'id': user['id'],
                'email': 'updated@example.com',
                'image_url': 'https://example.com/image.jpg'
            }
            _assert(
                _call_api(update_dict, 'user_update', True),
                False
            )


        def test_api_user_update_with_valid_image(self, _call_api, _assert):
            """Test that the API allows local image paths during user update."""
            user = factories.User(
                image_url='/images/default-user.png'
            )
            update_dict = {
                'id': user['id'],
                'email': 'updated@example.com',
                'image_url': '/images/updated-user.jpg'
            }
            _assert(
                _call_api(update_dict, 'user_update'),
                True,
                '/images/updated-user.jpg'
            )


        def test_api_user_create_without_image(self, _call_api, _assert):
            """Test that the API allows user creation without an image URL."""
            user_dict = {
                'name': 'testuser',
                'email': 'test@example.com',
                'password': 'SecurePassword123'
            }
            _assert(
                _call_api(user_dict, 'user_create'),
                True,
                expected_image_url=None
            )

        def test_api_user_update_remove_image(self, _call_api, _assert):
            """Test that the API allows removing image URL during user update."""
            user = factories.User(
                image_url='/images/default-user.png'
            )
            update_dict = {
                'id': user['id'],
                'email': 'updated@example.com',
                'image_url': ''
            }
            _assert(
                _call_api(update_dict, 'user_update'),
                True,
                expected_image_url=''
            )
