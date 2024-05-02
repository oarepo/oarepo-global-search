from invenio_records_resources.resources.records.config import RecordResourceConfig
from flask import current_app
from invenio_base.utils import obj_or_import_string
from flask_resources import ResponseHandler


class GlobalSearchResourceConfig(RecordResourceConfig):
    blueprint_name = "global_search"
    url_prefix = "/search"
    routes = {
        "list": "/",
    }

    @property
    def response_handlers(self):
        entrypoint_response_handlers = {}

        resource_defs = current_app.config.get("GLOBAL_SEARCH_MODELS")
        api_resources = []
        for definition in resource_defs:
            api_resource = obj_or_import_string(definition["api_resource_config"])
            api_resources.append(api_resource)
            handler = api_resource().response_handlers

        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                handler["application/vnd.inveniordm.v1+json"].serializer
            ),
            **super().response_handlers,
            **entrypoint_response_handlers,
        }

class GlobalUserSearchResourceConfig(RecordResourceConfig):
    blueprint_name = "global_user_search"
    url_prefix = "/user/search"
    routes = {
        "list": "/",
    }

    @property
    def response_handlers(self):
        entrypoint_response_handlers = {}

        resource_defs = current_app.config.get("GLOBAL_SEARCH_MODELS")
        api_resources = []
        for definition in resource_defs:
            api_resource = obj_or_import_string(definition["api_resource_config"])
            api_resources.append(api_resource)
            handler = api_resource().response_handlers

        # todo own Handler class
        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                handler["application/vnd.inveniordm.v1+json"].serializer
            ),
            **super().response_handlers,
            **entrypoint_response_handlers,
        }