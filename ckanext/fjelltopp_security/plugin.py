import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.fjelltopp_security.actions as fjelltopp_security_actions

log = logging.getLogger(__name__)


class FjelltoppSecurityPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IMiddleware, inherit=True)
    plugins.implements(plugins.IActions)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "fjelltopp-security")

    # IActions
    def get_actions(self):
        return {
            'user_update': fjelltopp_security_actions.validate_image_url_first,
            'user_create': fjelltopp_security_actions.validate_image_url_first,
            'group_update': fjelltopp_security_actions.validate_image_url_first,
            'group_create': fjelltopp_security_actions.validate_image_url_first,
            'organization_update': fjelltopp_security_actions.validate_image_url_first,
            'organization_create': fjelltopp_security_actions.validate_image_url_first,
        }

    # IMiddleware
    def make_middleware(self, app, config):
        @app.after_request
        def apply_owasp(response):
            response.headers["Strict-Transport-Security"] = config.get(
                "ckanext.fjelltopp_security.strict_transport_security",
                "max-age=31536000; preload",
            )
            response.headers["X-Content-Type-Options"] = config.get(
                "ckanext.fjelltopp_security.content_type_options", "nosniff"
            )
            response.headers["X-Permitted-Cross-Domain-Policies"] = config.get(
                "ckanext.fjelltopp_security.cross_domain_policies",
                "none",  # not sure about this one
            )
            response.headers["Referrer-Policy"] = config.get(
                "ckanext.fjelltopp_security.referrer_policy",
                "no-referrer-when-downgrade",  # this is default when not set
            )
            response.headers["Cache-Control"] = config.get(
                "ckanext.fjelltopp_security.cache_control",
                "",
            )
            response.headers["Cross-Origin-Opener-Policy"] = config.get(
                "ckanext.fjelltopp_security.coop", "same-site"
            )
            response.headers["Cross-Origin-Embedder-Policy"] = config.get(
                "ckanext.fjelltopp_security.coep", "unsafe-none"
            )
            response.headers["Cross-Origin-Resource-Policy"] = config.get(
                "ckanext.fjelltopp_security.corp", "cross-origin"
            )
            response.headers["Content-Security-Policy"] = config.get(
                "ckanext.fjelltopp_security.content_security_policy", ""
            )
            if ("Location" in response.headers) and (
                "logged_out_redirect" in response.headers["Location"]
            ):
                response.headers["Clear-Site-Data"] = '"*"'
            return response

        return app
