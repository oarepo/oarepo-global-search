import copy
from contextvars import ContextVar
from functools import cached_property

from deepmerge import always_merger
from flask import current_app, has_app_context
from invenio_base.utils import obj_or_import_string
from invenio_records_resources.records.systemfields import IndexField
from invenio_records_resources.services import RecordService as InvenioRecordService
from invenio_records_resources.services import (
    RecordServiceConfig as InvenioRecordServiceConfig,
)
from invenio_records_resources.services import pagination_links
from invenio_records_resources.services.records.params import (
    PaginationParam,
    QueryStrParam,
)
from oarepo_runtime.services.config.service import PermissionsPresetsConfigMixin
from oarepo_runtime.services.facets.params import GroupedFacetsParam
from oarepo_runtime.services.search import SearchOptions
from werkzeug.exceptions import Forbidden

from oarepo_global_search.services.records.permissions import (
    GlobalSearchPermissionPolicy,
)
from .api import GlobalSearchRecord
from .exceptions import InvalidServicesError
from .params import GlobalSearchStrParam
from .results import GlobalSearchResultList


class GlobalSearchOptions(SearchOptions):
    """Search options."""

    params_interpreters_cls = [
        QueryStrParam,
        PaginationParam,
        GroupedFacetsParam,
        GlobalSearchStrParam,
    ]

class GlobalSearchDraftsOptions(GlobalSearchOptions):
    """Search drafts options."""


"""
current_action = ContextVar("current_action")
current_config = ContextVar("current_config")
"""

class NoExecute:
    def __init__(self, query):
        self.query = query

    def execute(self):
        return self.query


class GlobalSearchService(InvenioRecordService):
    """GlobalSearchRecord service."""

    action = "search"

    def __init__(self):
        super().__init__(None)

    def indices(self):
        indices = []
        for service_dict in self.service_mapping:
            service = list(service_dict.keys())[0]
            indices.append(service.record_cls.index.search_alias)
            #if current_action.get("search") == "search_drafts" and getattr( # todo by default we search drafts too and there are other ways to eventually omit them than on index level?
            if getattr(service, "draft_cls", None):
                indices.append(service.draft_cls.index.search_alias)
        return indices

    def _search_opts_from_search_obj(self, search):
        facets = {}
        sort_options = {}

        facets.update(search.facets)
        try:
            sort_options.update(search.sort_options)
        except:
            pass
        sort_default = search.sort_default
        sort_default_no_query = search.sort_default_no_query
        facet_groups = search.facet_groups
        return {
            "facets": facets,
            "facet_groups": facet_groups,
            "sort_options": sort_options,
            "sort_default": sort_default,
            "sort_default_no_query": sort_default_no_query,
        }

    def _search_opts(self, config_field):
        ret = {}
        for service_dict in self.service_mapping:
            service = list(service_dict.keys())[0]
            if hasattr(service.config, config_field):
                ret = always_merger.merge(ret, self._search_opts_from_search_obj(getattr(service.config, config_field)))
        return ret

    def fill_search_opts(self, search_opts_cls, search_opts):
        search_opts_cls.facets = search_opts["facets"]
        search_opts_cls.facet_groups = search_opts["facet_groups"]
        search_opts_cls.sort_options = search_opts["sort_options"]
        search_opts_cls.sort_default = search_opts["sort_default"]
        search_opts_cls.sort_default_no_query = search_opts["sort_default_no_query"]
        return search_opts_cls

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
        """
        stored_config = current_config.get(None)
        if stored_config:
            return stored_config
        """

        GlobalSearchRecord.index = IndexField(self.indices())
        GlobalSearchResultList.services = self.service_mapping
        search_opts = self._search_opts("search")
        drafts_search_opts = self._search_opts("search_drafts")

        """
        url_prefix = "/user/search"
        url_prefix = "/search"
        """

        links_search = pagination_links("{+api}/search{?args*}")
        links_search_drafts = pagination_links("{+api}/user/search{?args*}")



        config_class = type(
            "GlobalSearchServiceConfig",
            (PermissionsPresetsConfigMixin, InvenioRecordServiceConfig),
            {
                "PERMISSIONS_PRESETS": ["everyone"],
                "base_permission_policy_cls": GlobalSearchPermissionPolicy,
                "result_list_cls": GlobalSearchResultList,
                "record_cls": GlobalSearchRecord,
                # "url_prefix": url_prefix,
                "links_search": links_search,
                "links_search_drafts": links_search_drafts,
                "search": self.fill_search_opts(GlobalSearchOptions, search_opts),
                "search_drafts": self.fill_search_opts(GlobalSearchDraftsOptions, drafts_search_opts),
            },
        )

        stored_config = config_class()
        # current_config.set(stored_config)

        return stored_config

    """
    @config.setter
    def config(self, value):
        pass
    """

    def search_drafts(
        self,
        identity,
        params,
        *args,
        extra_filter=None,
        search_preference=None,
        expand=False,
        **kwargs,
    ):
        drafts_search_opts = self._search_opts("search_drafts")
        result = self.global_search(
            identity,
            params,
            action="search_drafts",
            permission_action="read_draft",
            versioning=True,
            *args,
            extra_filter=extra_filter,
            search_preference=search_preference,
            expand=expand,
            search_opts=self.fill_search_opts(GlobalSearchDraftsOptions, drafts_search_opts),
            **kwargs,
        )
        result._links_tpl._links = self.config.links_search_drafts
        return result

    def search(
        self,
        identity,
        params,
        *args,
        extra_filter=None,
        search_preference=None,
        expand=False,
        **kwargs,
    ):
        return self.global_search(
            identity,
            params,
            action="search",
            permission_action="read",
            versioning=True,
            *args,
            extra_filter=extra_filter,
            search_preference=search_preference,
            expand=expand,
            **kwargs,
        )

    @cached_property
    def model_services(self):
        model_services = {}

        # check if search is possible
        for model in current_app.config.get("GLOBAL_SEARCH_MODELS", []):
            service_def = obj_or_import_string(model["model_service"])

            _service_cfg = obj_or_import_string(model["service_config"])
            if hasattr(_service_cfg, "build"):
                service_cfg = _service_cfg.build(current_app)
            else:
                service_cfg = _service_cfg()

            service = service_def(service_cfg)

            service_dict = {
                "record_cls": service.record_cls,
                "search_opts": service.config.search,
                "schema": service.record_cls.schema.value,
            }

            # Clone the service and patch its search method
            # to avoid querying OpenSearch and simply return the query.
            # This is wrapped in a function to ensure proper closure behavior.
            def patch_service(service):
                previous_search = service._search

                def _patched_search(*args, **kwargs):
                    ret = previous_search(*args, **kwargs)
                    return NoExecute(ret)

                def _patched_result_list(self, identity, results, params, **kwargs):
                    return results

                service._search = _patched_search
                service.result_list = _patched_result_list
                return service

            service = patch_service(service)
            
            model_services[service] = service_dict

        model_services = {service: v for service, v in model_services.items()}
        if model_services == {}:
            raise InvalidServicesError

        return model_services

    def global_search(
        self,
        identity,
        params,
        action,
        permission_action,
        versioning,
        *args,
        extra_filter=None,
        search_preference=None,
        search_opts=None,
        expand=False,
        **kwargs,
    ):
        """
        current_action.set(action)
        current_config.set(None)
        """

        model_services = self.model_services

        for service in list(model_services.keys()):
            if hasattr(service, "check_permission"):
                if not service.check_permission(identity, "search", **kwargs):
                    del model_services[service]
            else:
                del model_services[service]
        if model_services == {}:
            raise Forbidden()

        queries_list = {}
        for service, service_dict in model_services.items():

            if action == "search_drafts" and hasattr(service, "search_drafts"):
                search = service.search_drafts(
                    identity,
                    params=copy.deepcopy(params),
                    search_preference=search_preference,
                    expand=expand,
                    extra_filter=extra_filter,
                    **kwargs,
                )
            else:
                search = service.search(
                    identity,
                    params=copy.deepcopy(params),
                    search_preference=search_preference,
                    expand=expand,
                    extra_filter=extra_filter,
                    **kwargs,
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
        if "page" in params:
            combined_query["page"] = params["page"]
        if "size" in params:
            combined_query["size"] = params["size"]
        if "sort" in params:
            combined_query["sort"] = params["sort"]
        else:
            if "q" in params:
                combined_query["sort"] = search_opts.sort_default
            else:
                combined_query["sort"] = search_opts.sort_default_no_query

        hits = super().search(identity, params=combined_query, search_opts=search_opts)

        del hits._links_tpl.context["args"][
            "json"  # to get rid of the json arg from url
        ]
        if "sort" in params:
            hits._links_tpl.context["args"]["sort"] = params["sort"]

        # add the original parameters to the pagination links
        for param_name, param_value in params.items():
            if param_name != "facets":
                self.add_param_to_links(hits, param_name, param_value)
            else:
                for facet_name, facet_value in param_value.items():
                    self.add_param_to_links(hits, facet_name, facet_value)

        return hits

    def add_param_to_links(self, hits, param_name, param_value):
        if param_name not in hits._links_tpl.context["args"]:
            hits._links_tpl.context["args"][param_name] = param_value
