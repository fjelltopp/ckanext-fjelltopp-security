import pytest
from ckan.tests import factories
from ckan.plugins import toolkit
from ckan.logic import ValidationError


@pytest.mark.ckan_config("ckan.plugins", "fjelltopp_security")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestSecureOrganizationActions:

    @pytest.fixture
    def base_organization(self):
        """Create a basic organization with factories."""
        return factories.Organization(
            image_url='/images/test-org-image.jpg'
        )

    def test_organization_create_with_valid_data(self):
        """Test organization creation with valid local image URL succeeds."""
        org_dict = {
            'name': 'testorg',
            'title': 'Test Organization',
            'image_url': '/images/test-org-image.jpg'
        }
        organization = factories.Organization(**org_dict)

        assert organization['name'] == org_dict['name']
        assert organization['title'] == org_dict['title']
        assert organization['image_url'] == org_dict['image_url']

    @pytest.mark.parametrize("image_url", [
        'http://example.com/org-image.jpg',
        'https://example.com/org-image.jpg',
        '//example.com/org-image.jpg'
    ])

    def test_organization_create_with_external_image_fails(self, image_url):
        """Test organization creation fails with external image URLs."""
        with pytest.raises(ValidationError) as exception_info:
            factories.Organization(
                image_url=image_url
            )

        assert 'Image URL must be a local path. External URLs are not allowed' in str(exception_info.value)

    def test_organization_create_without_image_url(self):
        """Test organization creation succeeds without an image URL."""
        organization = factories.Organization(image_url=None)
        assert 'image_url' not in organization or not organization['image_url']

    def test_organization_update_with_valid_data(self, base_organization):
        """Test organization update with valid local image URL succeeds."""
        update_dict = {
            'id': base_organization['id'],
            'name': base_organization['name'],
            'title': 'Updated Test Organization',
            'image_url': '/images/updated-org-image.jpg'
        }
        updated_org = toolkit.get_action('organization_update')(
            context={'ignore_auth': True},
            data_dict=update_dict
        )
        assert updated_org['image_url'] == update_dict['image_url']
        assert updated_org['title'] == update_dict['title']

    def test_organization_update_without_image_url(self, base_organization):
        """Test organization update succeeds when not modifying image URL."""
        original_image_url = base_organization['image_url']
        update_dict = {
            'id': base_organization['id'],
            'name': base_organization['name'],
            'title': 'Updated Test Organization'
        }
        updated_org = toolkit.get_action('organization_update')(
            context={'ignore_auth': True},
            data_dict=update_dict
        )
        assert updated_org['image_url'] == original_image_url

    @pytest.mark.parametrize("image_url", [
        'http://example.com/org-image.jpg',
        'https://example.com/org-image.jpg',
        '//example.com/org-image.jpg'
    ])
    def test_organization_update_with_external_image_fails(self, base_organization, image_url):
        """Test organization update fails with external image URLs."""
        update_dict = {
            'id': base_organization['id'],
            'name': base_organization['name'],
            'title': 'Updated Test Organization',
            'image_url': image_url
        }
        with pytest.raises(ValidationError) as exception_info:
            toolkit.get_action('organization_update')(
                context={'ignore_auth': True},
                data_dict=update_dict
            )

        assert 'Image URL must be a local path. External URLs are not allowed' in str(exception_info.value)


@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
class TestSecureOrganizationAPI:

    def test_api_organization_create_with_external_image(self, _call_api, _assert):
        """Test that the API blocks external images during organization creation."""
        org_dict = {
            'name': 'test-org',
            'title': 'Test Organization',
            'image_url': 'https://example.com/image.jpg'
        }
        _assert(
            _call_api(org_dict, 'organization_create', True),
            False
        )

    def test_api_organization_update_with_external_image(self, _call_api, _assert):
        """Test that the API blocks external images during organization update."""
        org = factories.Organization(image_url='/images/original.jpg')
        update_dict = {
            'id': org['id'],
            'image_url': 'https://example.com/updated-image.jpg'
        }
        _assert(
            _call_api(update_dict, 'organization_update', True),
            False
        )


    def test_api_organization_update_with_valid_image(self, _call_api, _assert):
        """Test that the API allows local images during organization update."""
        org = factories.Organization(image_url='/images/original.jpg')
        update_dict = {
            'id': org['id'],
            'image_url': '/images/updated-image.jpg'
        }
        _assert(
            _call_api(update_dict, 'organization_update'),
            True,
            '/images/updated-image.jpg'
        )

    def test_api_organization_create_with_valid_image(self, _call_api, _assert):
        """Test that the API allows local images during organization creation."""
        org_dict = {
            'name': 'test-org',
            'title': 'Test Organization',
            'image_url': '/images/test-image.jpg'
        }
        _assert(
            _call_api(org_dict, 'organization_create'),
            True
        )

    def test_api_organization_create_without_image(self, _call_api, _assert):
        """Test that the API allows organization creation without an image URL."""
        org_dict = {
            'name': 'test-org',
            'title': 'Test Organization'
        }
        _assert(
            _call_api(org_dict, 'organization_create'),
            True,
            ''
        )

    def test_api_organization_update_remove_image(self, _call_api,_assert):
        """Test that the API allows removing image URL during update."""
        org = factories.Organization(image_url='/images/original.jpg')
        update_dict = {
            'id': org['id'],
            'image_url': ''
        }
        _assert(
            _call_api(update_dict, 'organization_update'),
            True,
            ''
        )
