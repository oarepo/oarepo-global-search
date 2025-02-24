from functools import cached_property

from deepmerge import always_merger
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

from oarepo_global_search.services.records.api import GlobalSearchRecord
from oarepo_global_search.services.records.params import GlobalSearchStrParam
from oarepo_global_search.services.records.permissions import (
    GlobalSearchPermissionPolicy,
)
from oarepo_global_search.services.records.results import GlobalSearchResultList
from oarepo_global_search.proxies import current_global_search


class GlobalSearchServiceConfig(PermissionsPresetsConfigMixin, InvenioRecordServiceConfig):
    """
    stored_config = current_config.get(None)
    if stored_config:
        return stored_config
    """

    base_permission_policy_cls = GlobalSearchPermissionPolicy
    PERMISSIONS_PRESETS = ["everyone"]
    result_list_cls = GlobalSearchResultList

    @property
    def search(self):
        return current_global_search.search

    @property
    def search_drafts(self):
        return current_global_search.search_drafts

    record_cls = GlobalSearchRecord
    links_search = pagination_links("{+api}/search{?args*}")
    links_search_drafts = pagination_links("{+api}/user/search{?args*}")


