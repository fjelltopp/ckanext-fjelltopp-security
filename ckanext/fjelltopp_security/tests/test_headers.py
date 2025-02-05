import pytest
from ckan.tests import factories
from ckan.plugins import toolkit
from ckan.common import config

@pytest.mark.ckan_config("ckan.plugins", "fjelltopp_security")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestSecurityMiddleware:

    def test_default_security_headers(self, app):
        url = toolkit.url_for('user.login')
        response = app.get(url)
        
        assert response.headers["Strict-Transport-Security"] == "max-age=31536000; preload"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Permitted-Cross-Domain-Policies"] == "none"
        assert response.headers["Referrer-Policy"] == "no-referrer-when-downgrade"
        assert response.headers["Cache-Control"] == "private"
        assert response.headers["Content-Security-Policy"] == ""
        assert response.headers["Cross-Origin-Opener-Policy"] == "same-site"
        assert response.headers["Cross-Origin-Embedder-Policy"] == "unsafe-none"
        assert response.headers["Cross-Origin-Resource-Policy"] == "cross-origin"


    @pytest.mark.ckan_config("ckanext.fjelltopp_security.strict_transport_security", "max-age=86400")
    @pytest.mark.ckan_config("ckanext.fjelltopp_security.content_type_options", "custom-value")
    @pytest.mark.ckan_config("ckanext.fjelltopp_security.cross_domain_policies", "custom-policy")
    @pytest.mark.ckan_config("ckanext.fjelltopp_security.referrer_policy", "same-origin")
    @pytest.mark.ckan_config("ckanext.fjelltopp_security.cache_control", "no-store")
    @pytest.mark.ckan_config("ckanext.fjelltopp_security.cross_origin_opener_policy", "same-origin")
    @pytest.mark.ckan_config("ckanext.fjelltopp_security.cross_origin_embedder_policy", "require-corp")
    @pytest.mark.ckan_config("ckanext.fjelltopp_security.cross_origin_resource_policy", "same-site")
    def test_custom_config_values(self, app):
        dataset = factories.Dataset()
        url = toolkit.url_for('dataset.read', id=dataset['name'])

        response = app.get(url)

        assert response.headers["Strict-Transport-Security"] == "max-age=86400"
        assert response.headers["X-Content-Type-Options"] == "custom-value"
        assert response.headers["X-Permitted-Cross-Domain-Policies"] == "custom-policy"
        assert response.headers["Referrer-Policy"] == "same-origin"
        # CKAN will make the Cache-Control private when the url requires a session
        assert response.headers["Cache-Control"] == "no-store, private"
        assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin"
        assert response.headers["Cross-Origin-Embedder-Policy"] == "require-corp"
        assert response.headers["Cross-Origin-Resource-Policy"] == "same-site"


    def test_clear_site_data_on_logout(self, app):
        @app.flask_app.route('/test_logout')
        def test_logout():
            response = app.flask_app.make_response('')
            response.headers['Location'] = '/logged_out_redirect'
            return response

        # Test the mock logout route
        response = app.get('/test_logout')

        # Verify the Clear-Site-Data header is set
        assert response.headers.get("Clear-Site-Data") == '"*"'


    def test_clear_site_data_not_set_without_redirect(self, app):
        @app.flask_app.route('/test_other_redirect')
        def test_other_redirect():
            response = app.flask_app.make_response('')
            response.headers['Location'] = '/some_other_page'
            return response

        # Test the mock route
        response = app.get('/test_other_redirect')

        # Verify the Clear-Site-Data header is not set
        assert "Clear-Site-Data" not in response.headers


    def test_no_clear_site_data_on_normal_response(self, app):
        dataset = factories.Dataset()
        url = toolkit.url_for('dataset.read', id=dataset['name'])

        response = app.get(url)

        assert "Clear-Site-Data" not in response.headers


    @pytest.mark.ckan_config("ckanext.fjelltopp_security.content_security_policy",
                             "default-src 'self'; script-src 'self' 'unsafe-inline'")
    def test_content_security_policy(self, app):
        dataset = factories.Dataset()
        url = toolkit.url_for('dataset.read', id=dataset['name'])

        response = app.get(url)

        expected_csp = "default-src 'self'; script-src 'self' 'unsafe-inline'"
        assert response.headers["Content-Security-Policy"] == expected_csp
