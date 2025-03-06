from invenio_records_resources.services.records.params import (
    PaginationParam,
)
from oarepo_runtime.services.facets.params import GroupedFacetsParam
from oarepo_runtime.services.search import SearchOptions

from oarepo_global_search.services.records.params import GlobalSearchStrParam


class GlobalSearchOptions(SearchOptions):
    """Search options."""

    params_interpreters_cls = [
        GroupedFacetsParam,
        PaginationParam,
        GlobalSearchStrParam,
    ]


class GlobalSearchDraftsOptions(GlobalSearchOptions):
    """Search drafts options."""
