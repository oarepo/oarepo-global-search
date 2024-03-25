from oarepo_ui.resources import RecordsUIResourceConfig, RecordsUIResource

from oarepo_global_search.proxies import current_global_search


class GlobalSearchUIResourceConfig(RecordsUIResourceConfig):
    blueprint_name = "global_search_ui"
    url_prefix = "/search"
    template_folder = "templates"

    templates = {
        "search": "global_search_ui.Search",
    }

    application_id = "global_search"

class GlobalSearchUIResource(RecordsUIResource):
    pass
