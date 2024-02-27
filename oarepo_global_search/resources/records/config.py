from invenio_records_resources.resources.records.config import RecordResourceConfig


class GlobalSearchResourceConfig(RecordResourceConfig):
    blueprint_name = "global_search"
    url_prefix = "/search"
    routes = {
        "list": "/",
    }


class GlobalUserSearchResourceConfig(RecordResourceConfig):
    blueprint_name = "global_user_search"
    url_prefix = "/user/search"
    routes = {
        "list": "/",
    }
