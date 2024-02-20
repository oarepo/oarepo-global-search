from invenio_records_resources.services import RecordService as InvenioRecordService
from flask import current_app
from invenio_base.utils import obj_or_import_string
import importlib_metadata
from invenio_records_resources.proxies import current_service_registry
# from global_search.proxies import current_service as search_service
from oarepo_runtime.services.config.service import PermissionsPresetsConfigMixin
from oarepo_runtime.services.results import RecordList
from invenio_records_resources.records.systemfields import IndexField
from invenio_records_resources.services import (
    RecordServiceConfig as InvenioRecordServiceConfig,
)
import time

from .params import GlobalSearchStrParam
from .results import GlobalSearchResultList
from invenio_records_resources.records.api import Record
from oarepo_global_search.services.records.permissions import GlobalSearchPermissionPolicy


class GlobalSearchService(InvenioRecordService):
    """GlobalSearchRecord service."""

    def __init__(self, identity, params, **kwargs):
        self.identity = identity
        self.params = params
        # self.__super__(**kwargs)

    def get_model_services(self):
        services = []
        models = []
        model_services = []
        import copy

        # get all services
        for var in current_service_registry._services:
            services.append(current_service_registry._services[var])

        # get all model_services }todo dedeni
        for var in current_app.config:
            if var.endswith("SERVICE_CLASS") and var != "GLOBAL_SEARCH_RECORD_SERVICE_CLASS":
                models.append(current_app.config[var])

        # get search services for models

        for s in services:
            if s.__class__ in models:
                model_services.append(s)

        return model_services

    def indices(self):
        services = self.get_model_services()
        indices = []
        for s in services:
            indices.append(s.record_cls.index.search_alias)
        return indices

    @property
    def service_mapping(self):
        services = self.get_model_services()
        service_mapping = []
        for s in services:
            service_mapping.append({s: s.record_cls.schema.value})
        return service_mapping

    @property
    def config(self):
        Record.index = IndexField(self.indices())
        GlobalSearchResultList.services = self.service_mapping

        config_class = type("GlobalSearchServiceConfig",
                            (PermissionsPresetsConfigMixin, InvenioRecordServiceConfig),
                            {"PERMISSIONS_PRESETS": ["everyone"],
                             "base_permission_policy_cls": GlobalSearchPermissionPolicy,
                             "result_list_cls": GlobalSearchResultList,
                             "record_cls" : Record

                             }
                            )
        return config_class()

    def global_search(self):
        identity = self.identity
        params = self.params

        model_services = []
        models = []

        services = self.get_model_services()

        for var in current_app.config:
            if var.endswith("SERVICE_CLASS") and var != "GLOBAL_SEARCH_RECORD_SERVICE_CLASS":
                models.append(current_app.config[var])

        for s in services:
            if s.__class__ in models:
                model_services.append({s: {}})

        #check if search is possible
        for ms in model_services:
            service = list(ms.keys())[0]
            try:
                service.create_search(identity= identity, record_cls=service.record_cls, search_opts=service.config.search)
                ms[service]["record_cls"] =  service.record_cls
                ms[service]["search_opts"] = service.config.search
                ms[service]["schema"] = service.record_cls.schema.value
            except Exception as e:
                print(e)


        #check permissions
        for ms in model_services:
            service = list(ms.keys())[0]
            if not service.check_permission(identity, "search"):
                model_services.remove(ms)

        #get queries
        queries_list = []
        for ms in model_services:
            service = list(ms.keys())[0]
            query = service.search_request(identity=identity, params=params, record_cls=ms[service]["record_cls"], search_opts=ms[service]["search_opts"])
            queries_list.append({ms[service]["schema"]: query.to_dict()})

        #merge query
        combined_query = {
            "query": {
                "bool": {
                    "should": [], "minimum_should_match": 1
                }
            },
            "aggs": {},
            "post_filter": {},
            "sort": []
        }
        for query_dict in queries_list:
            schema_name, query_data = list(query_dict.items())[0]
            schema_query = query_data.get('query', {})
            combined_query["query"]["bool"]["should"].append({
                "bool": {
                    "must": [
                        {"term": {"$schema": schema_name}},
                        schema_query
                    ]
                }
            })

            if 'aggs' in query_data:
                for agg_key, agg_value in query_data['aggs'].items():
                    combined_query["aggs"][agg_key] = agg_value
            if "post_filter" in query_data:
                for post_key, post_value in query_data['post_filter'].items():
                    combined_query["post_filter"][post_key] = post_value
            if "sort" in query_data:
                combined_query["sort"].extend(query_data["sort"])

        combined_query = {"json": combined_query}

        self.config.search.params_interpreters_cls.append(GlobalSearchStrParam)
        hits = self.search(identity, params=combined_query)

        return hits

