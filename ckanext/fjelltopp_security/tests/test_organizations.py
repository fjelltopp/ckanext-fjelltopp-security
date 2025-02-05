import pytest
from ckan.tests import factories
from ckan.plugins import toolkit
from ckan.logic import ValidationError
from ckan.tests.helpers import call_action


@pytest.mark.ckan_config("ckan.plugins", "fjelltopp_security")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestSecureOrganizationActions:

    def test_organization_create_with_valid_data(self, context):
        org_dict = {
            'name': 'testorg',
            'title': 'Test Organization',
            'image_url': '/images/test-org-image.jpg'
        }
        created_org = call_action('organization_create', context=context, **org_dict)
        assert created_org['image_url'] == org_dict['image_url']


    @pytest.mark.parametrize("image_url", [
        'http://example.com/org-image.jpg',
        'https://example.com/org-image.jpg',
        '//example.com/org-image.jpg'
    ])
    def test_organization_create_with_external_image_fails(self, image_url, context):
        org_dict = {
            'name': 'testorg',
            'title': 'Test Organization',
            'image_url': 'https://example.com/org-image.jpg'
        }
        with pytest.raises(ValidationError):
            call_action('organization_create', context=context, **org_dict)


    def test_organization_create_without_image_url(self, context):
        org_dict = {
            'name': 'testorg',
            'title': 'Test Organization'
        }
        created_org = call_action('organization_create', context=context, **org_dict)
        assert 'image_url' not in created_org or not created_org['image_url']


    def test_organization_update_with_valid_data(self, organization):
        update_dict = {
            'id': organization['id'],
            'name': organization['name'],
            'title': 'Updated Test Organization',
            'image_url': '/images/updated-org-image.jpg'
        }
        updated_org = call_action('organization_update', **update_dict)
        assert updated_org['image_url'] == update_dict['image_url']


    def test_organization_update_without_image_url(self, organization):
        original_image_url = organization['image_url']
        update_dict = {
            'id': organization['id'],
            'name': organization['name'],
            'title': 'Updated Test Organization'
        }
        updated_org = call_action('organization_update', **update_dict)
        assert updated_org['image_url'] == original_image_url

    @pytest.mark.parametrize("image_url", [
        'http://example.com/org-image.jpg',
        'https://example.com/org-image.jpg',
        '//example.com/org-image.jpg'
    ])
    def test_organization_update_with_external_image_fails(self, organization, image_url):
        update_dict = {
            'id': organization['id'],
            'name': organization['name'],
            'title': 'Updated Test Organization',
            'image_url': image_url
        }
        with pytest.raises(ValidationError) as exception_info:
            call_action('organization_update', **update_dict)
