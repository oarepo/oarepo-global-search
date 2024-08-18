from oarepo_runtime.info.views import api_url_for


class GlobalSearchInfoComponent:
    def __init__(self, info_resource):
        pass

    def repository(self, *, data):
        data["links"]["records"] = api_url_for(f"global_search.search", _external=True)
        data["links"]["user_records"] = api_url_for(
            f"global_user_search.search", _external=True
        )