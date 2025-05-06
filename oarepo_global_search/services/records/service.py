import copy
from functools import cached_property

from flask import current_app
from invenio_records_resources.services import RecordService as InvenioRecordService
from werkzeug.exceptions import Forbidden

from oarepo_global_search.proxies import current_global_search

from .exceptions import InvalidServicesError


class NoExecute:
    def __init__(self, query):
        self.query = query

    def execute(self):
        return self.query


class GlobalSearchService(InvenioRecordService):
    """GlobalSearchRecord service."""

    action = "search"

    @property
    def indexer(self):
        return None

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
            search_opts=self.config.search_drafts,
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
            search_opts=self.config.search,
            **kwargs,
        )

    def search_all_records(
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
            action="search_all_records",
            permission_action="read_all_records",
            versioning=True,
            *args,
            extra_filter=extra_filter,
            search_preference=search_preference,
            expand=expand,
            search_opts=getattr(self.config, "search_all_records", None)
            or self.config.search_drafts,
            **kwargs,
        )

    def _patch_service(self, service):
        # Clone the service and patch its search method
        # to avoid querying OpenSearch and simply return the query.
        # This is wrapped in a function to ensure proper closure behavior.
        previous_search = service._search

        def _patched_search(*args, **kwargs):
            ret = previous_search(*args, **kwargs)
            return NoExecute(ret)

        def _patched_result_list(self, identity, results, params, **kwargs):
            return results

        service._search = _patched_search
        service.result_list = _patched_result_list
        return service

    @cached_property
    def patched_services(self):
        patched_services = []

        # check if search is possible
        for service in current_global_search.global_search_model_services:
            patched = copy.deepcopy(service)
            patched = self._patch_service(patched)
            patched_services.append(patched)

        if not patched_services:
            raise InvalidServicesError

        return patched_services

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
        model_services = [*self.patched_services]

        for idx in range(len(model_services) - 1, -1, -1):
            service = model_services[idx]

            if hasattr(service, "check_permission"):
                if not service.check_permission(identity, "search", **kwargs):
                    del model_services[idx]
            else:
                del model_services[idx]

            for model_settings in current_app.config.get("GLOBAL_SEARCH_MODELS", []):
                service_name = (
                    f"{type(service).__module__}.{type(service).__qualname__}"
                )
                if service_name == model_settings["model_service"]:
                    if model_settings.get(action, True) is False:
                        del model_services[idx]
                    break

        if model_services == {}:
            raise Forbidden()

        queries_list = {}
        for service in model_services:
            if action == "search_drafts" and hasattr(service, "search_drafts"):
                search = service.search_drafts(
                    identity,
                    params=copy.deepcopy(params),
                    search_preference=search_preference,
                    expand=expand,
                    extra_filter=extra_filter,
                    **kwargs,
                )
            elif action == "search_all_records" and hasattr(
                service, "search_all_records"
            ):
                search = service.search_all_records(
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
            queries_list[service.record_cls.schema.value] = search.to_dict()

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
            if "q" in params and params["q"]:
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

    def scan(
        self, identity, params=None, search_preference=None, expand=False, **kwargs
    ):
        results = []
        for service in current_global_search.global_search_model_services:
            results.append(
                service.scan(
                    identity,
                    params=params,
                    search_preference=search_preference,
                    expand=expand,
                    **kwargs,
                )
            )
        return self.config.scan_result_list_cls(results)

    def add_param_to_links(self, hits, param_name, param_value):
        if param_name not in hits._links_tpl.context["args"]:
            hits._links_tpl.context["args"][param_name] = param_value
