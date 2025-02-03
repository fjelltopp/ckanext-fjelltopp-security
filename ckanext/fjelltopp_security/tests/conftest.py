import pytest
from ckan.tests import factories
from ckan.plugins import toolkit


@pytest.fixture()
def _call_api(app):
    def _make_api_call(data_dict, fn, expect_error=False):
        sysadmin = factories.Sysadmin(image_url='')
        env = {'REMOTE_USER': sysadmin['name']}
        url = toolkit.url_for('api.action', ver=3, logic_function=fn)
        response = app.post(
            url,
            json=data_dict,
            extra_environ=env,
            expect_errors=expect_error
        )
        return response
    return _make_api_call


@pytest.fixture()
def _assert():
    def _assert_function(response,
                        success=True,
                        expected_image_url='/images/test-image.jpg'):
        if success:
            assert response.status_code == 200
            result = response.json
            assert result['success'] is True
            assert result['result']['image_url'] == expected_image_url
        else:
            assert response.status_code == 409
            error_dict = response.json
            assert error_dict['success'] is False
            assert 'Image URL must be a local path' in str(error_dict['error'])
    return _assert_function
