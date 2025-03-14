from flask import current_app, g
from invenio_base.utils import obj_or_import_string
from invenio_records_resources.resources.records.resource import request_search_args
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.resources import RecordsUIResource, RecordsUIResourceConfig

no_models_template = "global_search.NoModels"


class GlobalSearchUIResourceConfig(RecordsUIResourceConfig):
    blueprint_name = "global_search_ui"
    url_prefix = "/search"
    template_folder = "templates"
    api_service = "records"
    templates = {
        "search": "global_search.Search",
        "no-models": no_models_template,
    }

    application_id = "global_search"

    @property
    def default_components(self):
        resource_defs = current_app.config.get("GLOBAL_SEARCH_MODELS")
        default_components = {}
        for definition in resource_defs:
            ui_resource = obj_or_import_string(definition["ui_resource_config"])
            service_def = obj_or_import_string(definition["model_service"])
            service_cfg = obj_or_import_string(definition["service_config"])
            service = service_def(service_cfg())
            default_components[service.record_cls.schema.value] = getattr(
                ui_resource, "search_component", None
            )
        return default_components

    def search_endpoint_url(self, identity, api_config, overrides={}, **kwargs):
        api_url = current_app.config.get("GLOBAL_SEARCH_API_URL", None)
        if api_url:
            return api_url
        return super().search_endpoint_url(identity, api_config, overrides, **kwargs)

class GlobalSearchUIResource(RecordsUIResource):
    @request_search_args
    def search(self):
        if len(current_app.config.get("GLOBAL_SEARCH_MODELS")) == 0:
            return current_oarepo_ui.catalog.render(
                self.get_jinjax_macro(
                    "no-models",
                    identity=g.identity,
                    default_macro=no_models_template,
                )
            )

        return super().search()

    @request_search_args
    def search_without_slash(self):
        if len(current_app.config.get("GLOBAL_SEARCH_MODELS")) == 0:
            return current_oarepo_ui.catalog.render(
                self.get_jinjax_macro(
                    "no-models",
                    identity=g.identity,
                    default_macro=no_models_template,
                )
            )

        return super().search_without_slash()


def create_blueprint(app):
    """Register blueprint for this resource."""
    return GlobalSearchUIResource(GlobalSearchUIResourceConfig()).as_blueprint()
