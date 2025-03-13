from flask import current_app
from invenio_base.utils import obj_or_import_string
from invenio_drafts_resources.resources.records.args import SearchRequestArgsSchema
from invenio_records_resources.resources.records.config import RecordResourceConfig

from .response import GlobalSearchResponseHandler


class GlobalSearchResourceConfig(RecordResourceConfig):
    blueprint_name = "global_search"
    url_prefix = "/"
    routes = {
        "list": "/search/",
        "user-list": "/user/search/",
        "all-list": "/all/search/",
    }
    request_search_args = SearchRequestArgsSchema

    @property
    def response_handlers(self):
        entrypoint_response_handlers = {}

        resource_defs = current_app.config.get("GLOBAL_SEARCH_MODELS")
        serializers = []

        for definition in resource_defs:
            api_resource = obj_or_import_string(definition["api_resource_config"])
            handler = api_resource().response_handlers
            service_def = obj_or_import_string(definition["model_service"])
            service_cfg = obj_or_import_string(definition["service_config"])
            service = service_def(service_cfg())
            serializers.append(
                {
                    "schema": service.record_cls.schema.value,
                    "serializer": handler[
                        "application/vnd.inveniordm.v1+json"
                    ].serializer,
                }
            )

        return {
            "application/vnd.inveniordm.v1+json": GlobalSearchResponseHandler(
                serializers
            ),
            **super().response_handlers,
            **entrypoint_response_handlers,
        }
