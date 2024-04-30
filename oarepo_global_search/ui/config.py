from oarepo_ui.resources import RecordsUIResourceConfig, RecordsUIResource
from flask import current_app
from invenio_base.utils import obj_or_import_string


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
            record_api = obj_or_import_string(definition["records_api"])
            default_components[record_api.schema.value] = ui_resource.search_component
        return default_components

class GlobalSearchUIResource(RecordsUIResource):
    pass


def create_blueprint(app):
    """Register blueprint for this resource."""
    return GlobalSearchUIResource(GlobalSearchUIResourceConfig()).as_blueprint()