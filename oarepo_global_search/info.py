from oarepo_runtime.info.views import api_url_for


class GlobalSearchInfoComponent:
    def __init__(self, info_resource):
        pass

    def repository(self, *, data):
        data["links"]["records"] = api_url_for("global_search.search", _external=True)
        data["links"]["drafts"] = api_url_for(
            "global_search.search_user", _external=True
        )
