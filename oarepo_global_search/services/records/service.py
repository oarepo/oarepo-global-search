import copy

from invenio_records_resources.records.api import Record
from invenio_records_resources.records.systemfields import IndexField
from invenio_records_resources.services import RecordService as InvenioRecordService
from invenio_records_resources.services import (
    RecordServiceConfig as InvenioRecordServiceConfig,
)
from invenio_records_resources.services import pagination_links
from oarepo_runtime.services.config.service import PermissionsPresetsConfigMixin

from oarepo_global_search.services.records.permissions import (
    GlobalSearchPermissionPolicy,
)

from ...proxies import current_global_search
from .params import GlobalSearchStrParam
from .results import GlobalSearchResultList


class GlobalSearchService(InvenioRecordService):
    """GlobalSearchRecord service."""

    def __init__(self):
        super().__init__(None)

    def indices(self):
        indices = []
        for s in current_global_search.model_services:
            indices.append(s.record_cls.index.search_alias)
        return indices

    @property
    def service_mapping(self):
        service_mapping = []
        for s in current_global_search.model_services:
            service_mapping.append({s: s.record_cls.schema.value})
        return service_mapping

    @property
    def config(self):
        Record.index = IndexField(self.indices())
        GlobalSearchResultList.services = self.service_mapping

        config_class = type(
            "GlobalSearchServiceConfig",
            (PermissionsPresetsConfigMixin, InvenioRecordServiceConfig),
            {
                "PERMISSIONS_PRESETS": ["everyone"],
                "base_permission_policy_cls": GlobalSearchPermissionPolicy,
                "result_list_cls": GlobalSearchResultList,
                "record_cls": Record,
                # todo is there a use case where this would affect any other links??
                "links_search": pagination_links("{+api}/search{?args*}"),
            },
        )
        return config_class()

    @config.setter
    def config(self, value):
        pass

    def global_search(self, identity, params):
        model_services = {}

        # check if search is possible
        for service in current_global_search.model_services:
            try:
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
            except Exception as e:
                print(e)

        model_services = {
            service: v
            for service, v in model_services.items()
            if not hasattr(service, "check_permission")
            or service.check_permission(identity, "search")
        }
        # get queries
        queries_list = {}
        for service, service_dict in model_services.items():
            query = service.search_request(
                identity=identity,
                params=copy.deepcopy(params),
                record_cls=service_dict["record_cls"],
                search_opts=service_dict["search_opts"],
            )
            queries_list[service_dict["schema"]] = query.to_dict()

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
