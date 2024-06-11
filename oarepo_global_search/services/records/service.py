import copy
from flask import current_app, has_app_context
from invenio_base.utils import obj_or_import_string
from invenio_records_resources.records.systemfields import IndexField
from invenio_records_resources.services import RecordService as InvenioRecordService
from invenio_records_resources.services import (
    RecordServiceConfig as InvenioRecordServiceConfig,
)
from invenio_records_resources.services import SearchOptions, pagination_links
from oarepo_runtime.services.config.service import PermissionsPresetsConfigMixin

from oarepo_global_search.services.records.permissions import (
    GlobalSearchPermissionPolicy,
)

from .api import GlobalSearchRecord
from .params import GlobalSearchStrParam
from .results import GlobalSearchResultList

# from invenio_records_resources.records.api import Record




class GlobalSearchOptions(SearchOptions):
    """Search options."""



class GlobalSearchService(InvenioRecordService):
    """GlobalSearchRecord service."""

    components_def = None

    def __init__(self):
        super().__init__(None)

    def indices(self):
        indices = []
        for service_dict in self.service_mapping:
            service = list(service_dict.keys())[0]
            indices.append(service.record_cls.index.search_alias)
        return indices

    def search_opts(self):
        facets = {}
        sort_options = {}
        sort_default = ""
        sort_default_no_query = ""
        for service_dict in self.service_mapping:
            service = list(service_dict.keys())[0]
            facets.update(service.config.search.facets)
            try:
                sort_options.update(service.config.search.sort_options)
            except:
                pass
            sort_default = service.config.search.sort_default
            sort_default_no_query = service.config.search.sort_default_no_query
        return {
            "facets": facets,
            "sort_options": sort_options,
            "sort_default": sort_default,
            "sort_default_no_query": sort_default_no_query,
        }

    @property
    def indexer(self):
        return None

    @property
    def service_mapping(self):
        service_mapping = []
        if has_app_context() and hasattr(current_app, "config"):
            for model in current_app.config.get("GLOBAL_SEARCH_MODELS", []):
                service_def = obj_or_import_string(model["model_service"])
                service_cfg = obj_or_import_string(model["service_config"])
                service = service_def(service_cfg())
                service_mapping.append({service: service.record_cls.schema.value})

        return service_mapping

    @property
    def config(self):
        GlobalSearchRecord.index = IndexField(self.indices())
        GlobalSearchResultList.services = self.service_mapping
        search_opts = self.search_opts()
        GlobalSearchOptions.facets = search_opts["facets"]
        GlobalSearchOptions.sort_options = search_opts["sort_options"]
        GlobalSearchOptions.sort_default = search_opts["sort_default"]
        GlobalSearchOptions.sort_default_no_query = search_opts["sort_default_no_query"]

        config_class = type(
            "GlobalSearchServiceConfig",
            (PermissionsPresetsConfigMixin, InvenioRecordServiceConfig),
            {
                "PERMISSIONS_PRESETS": ["everyone"],
                "base_permission_policy_cls": GlobalSearchPermissionPolicy,
                "result_list_cls": GlobalSearchResultList,
                "record_cls": GlobalSearchRecord,
                "url_prefix": "/search",
                "links_search": pagination_links("{+api}/search{?args*}"),
                "search": GlobalSearchOptions,
            },
        )
        return config_class()

    @config.setter
    def config(self, value):
        pass

    def global_search(self, identity, params, *args, extra_filter=None, **kwargs):
        model_services = {}

        # check if search is possible
        for model in current_app.config.get("GLOBAL_SEARCH_MODELS"):
            service_def = obj_or_import_string(model["model_service"])
            service_cfg = obj_or_import_string(model["service_config"])
            service = service_def(service_cfg)

            service.create_search(
                identity=identity,
                record_cls=service.record_cls,
                search_opts=service.config.search,
            )
            service_dict = {
                "record_cls": service.record_cls,
                "search_opts": service.config.search,
                "schema": service.record_cls.schema.value,
            }
            model_services[service] = service_dict

        model_services = {
            service: v
            for service, v in model_services.items()
            if not hasattr(service, "check_permission")
            or service.check_permission(identity, "search", **kwargs)
        }
        # get queries
        queries_list = {}
        for service, service_dict in model_services.items():
            search = service.search_request(
                identity=identity,
                params=copy.deepcopy(params),
                record_cls=service_dict["record_cls"],
                search_opts=service_dict["search_opts"],
                extra_filter=extra_filter,
            )
            if self.components_def:
                for component in service.components:
                    if hasattr(component, "search"):
                        search = getattr(component, "search")(identity, search, params)
                for component in service.components:
                    if hasattr(component, "search_drafts"):
                        search = getattr(component, "search_drafts")(
                            identity, search, params
                        )
            queries_list[service_dict["schema"]] = search.to_dict()

        # merge query
        combined_query = {
            "query": {"bool": {"should": [], "minimum_should_match": 1}},
            "aggs": {},
            "post_filter": {},
            "sort": [],
        }
        for schema_name, query_data in queries_list.items():
            schema_query = query_data.get("query", {})
            combined_query["query"]["bool"]["should"].append(
                {"bool": {"must": [{"term": {"$schema": schema_name}}, schema_query]}}
            )

            if "aggs" in query_data:
                for agg_key, agg_value in query_data["aggs"].items():
                    combined_query["aggs"][agg_key] = agg_value
            if "post_filter" in query_data:
                for post_key, post_value in query_data["post_filter"].items():
                    combined_query["post_filter"][post_key] = post_value
            if "sort" in query_data:
                combined_query["sort"].extend(query_data["sort"])

        combined_query = {"json": combined_query}

        self.config.search.params_interpreters_cls.append(GlobalSearchStrParam)
        hits = self.search(identity, params=combined_query)

        del hits._links_tpl.context["args"][
            "json"
        ]  # to get rid of the json arg from url

        return hits
