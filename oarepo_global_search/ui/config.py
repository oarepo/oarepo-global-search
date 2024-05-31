from flask import current_app
from invenio_base.utils import obj_or_import_string
from oarepo_ui.resources import RecordsUIResource, RecordsUIResourceConfig


class GlobalSearchUIResourceConfig(RecordsUIResourceConfig):
    blueprint_name = "global_search_ui"
    url_prefix = "/search"
    template_folder = "templates"
    api_service = "records"
    templates = {
        "search": "global_search.Search",
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


class GlobalSearchUIResource(RecordsUIResource):
    pass


def create_blueprint(app):
    """Register blueprint for this resource."""
    return GlobalSearchUIResource(GlobalSearchUIResourceConfig()).as_blueprint()
