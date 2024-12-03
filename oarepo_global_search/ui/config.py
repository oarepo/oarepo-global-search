from flask import current_app, g
from invenio_base.utils import obj_or_import_string
from oarepo_ui.resources import RecordsUIResource, RecordsUIResourceConfig
from oarepo_ui.proxies import current_oarepo_ui
from invenio_records_resources.resources.records.resource import request_search_args


class GlobalSearchUIResourceConfig(RecordsUIResourceConfig):
    blueprint_name = "global_search_ui"
    url_prefix = "/search"
    template_folder = "templates"
    api_service = "records"
    templates = {
        "search": "global_search.Search",
        "no-models": "global_search.NoModels",
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
            resource_components = getattr(ui_resource, "search_components", None)
            if resource_components:
                for key, value in resource_components.items():
                    if key == "ResultsList.item" or key == "ResultsGrid.item":
                        key_with_schema = f"{key}.{service.record_cls.schema.value}"
                        default_components[key_with_schema] = value
                    else:
                        default_components[key] = value
        return default_components


class GlobalSearchUIResource(RecordsUIResource):
    @request_search_args
    def search(self):
        if len(current_app.config.get("GLOBAL_SEARCH_MODELS")) == 0:
            return current_oarepo_ui.catalog.render(
                self.get_jinjax_macro(
                    "no-models",
                    identity=g.identity,
                )
            )

        return super().search()


def create_blueprint(app):
    """Register blueprint for this resource."""
    return GlobalSearchUIResource(GlobalSearchUIResourceConfig()).as_blueprint()
