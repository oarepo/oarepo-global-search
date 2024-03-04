from oarepo_global_search.proxies import current_global_search
from oarepo_global_search.services.records.service import GlobalSearchService


class GlobalUserSearchService(GlobalSearchService):
    """GlobalSearchRecord service."""

    def indices(self):
        indices = []
        for s in current_global_search.model_services:
            indices.append(s.record_cls.index.search_alias)
            indices.append(s.draft_cls.index.search_alias)
        return indices
