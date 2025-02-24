from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from invenio_base.utils import obj_or_import_string
from invenio_records_resources.records.systemfields import IndexField

from oarepo_global_search.resources.records.config import (
    GlobalSearchResourceConfig,
)
from oarepo_global_search.resources.records.resource import GlobalSearchResource
from oarepo_global_search.services.records.config import GlobalSearchServiceConfig
from oarepo_global_search.services.records.search import (
    GlobalSearchDraftsOptions,
    GlobalSearchOptions,
)
from oarepo_global_search.services.records.service import GlobalSearchService
from oarepo_global_search.ui.config import (
    GlobalSearchUIResource,
    GlobalSearchUIResourceConfig,
)

if TYPE_CHECKING:
    from flask import Flask

from functools import cached_property

from deepmerge import always_merger

from oarepo_global_search.proxies import current_global_search
from oarepo_global_search.services.records.api import GlobalSearchRecord
from oarepo_global_search.services.records.results import GlobalSearchResultList


class OARepoGlobalSearch(object):
    """OARepo DOI extension."""

    global_search_resource: GlobalSearchResource = None

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_config(app)
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.app = app
        self.init_services(app)
        self.init_resources(app)
        app.extensions["global_search"] = self

    """
    # todo what is the point of this?
    @functools.cached_property
    def model_services(self):
        # load all models from json files registered in oarepo.ui entry point
        ret = []
        eps = entry_points(group="oarepo.models")

        for ep in eps:
            path = Path(obj_or_import_string(ep.module).__file__).parent / ep.attr
            model = json.loads(path.read_text())
            service_id = (
                model.get("model", {}).get("service-config", {}).get("service-id")
            )
            if service_id and service_id in current_service_registry._services:
                ret.append(current_service_registry.get(service_id))
        return ret
    """

    def init_services(self, app):
        self.service = GlobalSearchService(GlobalSearchServiceConfig())
        app.extensions["global_search_service"] = self.service

    def init_resources(self, app):
        """Init resources."""
        self.global_search_resource = GlobalSearchResource(
            config=GlobalSearchResourceConfig(), service=self.service
        )
        self.global_search_ui_resource = GlobalSearchUIResource(
            config=GlobalSearchUIResourceConfig()
        )

    def init_config(self, app):
        app.config.setdefault("INFO_ENDPOINT_COMPONENTS", []).append(
            "oarepo_global_search.info:GlobalSearchInfoComponent"
        )

    @functools.cached_property
    def service_mapping(self):
        service_mapping = []
        if hasattr(self.app, "config"):
            for model in self.app.config.get("GLOBAL_SEARCH_MODELS", []):
                service_def = obj_or_import_string(model["model_service"])
                service_cfg = obj_or_import_string(model["service_config"])
                service = service_def(service_cfg())
                service_mapping.append(service)

        return service_mapping

    @functools.cached_property
    def indices(self):
        indices = []
        for service in self.service_mapping:
            indices.append(service.record_cls.index.search_alias)
            # if current_action.get("search") == "search_drafts" and getattr( # todo by default we search drafts too and there are other ways to eventually omit them than on index level?
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
        for service in current_global_search.service_mapping:
            if hasattr(service.config, config_field):
                ret = always_merger.merge(
                    ret,
                    self._search_opts_from_search_obj(
                        getattr(service.config, config_field)
                    ),
                )
        return ret

    def _fill_search_opts(self, search_opts_cls, search_opts):
        search_opts_cls.facets = search_opts["facets"]
        search_opts_cls.facet_groups = search_opts["facet_groups"]
        search_opts_cls.sort_options = search_opts["sort_options"]
        search_opts_cls.sort_default = search_opts["sort_default"]
        search_opts_cls.sort_default_no_query = search_opts["sort_default_no_query"]
        return search_opts_cls

    @cached_property
    def search(self):
        return self._fill_search_opts(GlobalSearchOptions, self._search_opts("search"))

    @cached_property
    def search_drafts(self):
        return self._fill_search_opts(
            GlobalSearchDraftsOptions, self._search_opts("search_drafts")
        )


def api_finalize_app(app: Flask) -> None:
    """Finalize app."""
    finalize_app(app)


def finalize_app(app: Flask) -> None:
    """Finalize app."""
    ext = app.extensions["global_search"]
    GlobalSearchRecord.index = IndexField(ext.indices)
    GlobalSearchResultList.services = ext.service_mapping
