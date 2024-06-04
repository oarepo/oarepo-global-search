import functools
import json
from pathlib import Path

from importlib_metadata import entry_points
from invenio_base.utils import obj_or_import_string
from invenio_records_resources.proxies import current_service_registry

from oarepo_global_search import config
from oarepo_global_search.resources.records.config import (
    GlobalSearchResourceConfig,
    GlobalUserSearchResourceConfig,
)
from oarepo_global_search.resources.records.resource import GlobalSearchResource
from oarepo_global_search.services.records.service import GlobalSearchService
from oarepo_global_search.services.records.user_service import GlobalUserSearchService
from oarepo_global_search.ui.config import (
    GlobalSearchUIResource,
    GlobalSearchUIResourceConfig,
)


class OARepoGlobalSearch(object):
    """OARepo DOI extension."""

    global_search_resource: GlobalSearchResource = None
    global_user_search_resource: GlobalSearchResource = None

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.app = app
        self.init_resources(app)
        app.extensions["global_search"] = self

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


    def init_resources(self, app):
        """Init resources."""
        self.global_search_resource = GlobalSearchResource(
            config=GlobalSearchResourceConfig(), service=GlobalSearchService()
        )
        self.global_user_search_resource = GlobalSearchResource(
            config=GlobalUserSearchResourceConfig(), service=GlobalUserSearchService()
        )
        self.global_search_ui_resource = GlobalSearchUIResource(
            config=GlobalSearchUIResourceConfig()
        )

    @functools.cached_property
    def service_records(self):
        return config.GLOBAL_SEARCH_RECORD_SERVICE_CLASS()
