from flask import current_app
from werkzeug.local import LocalProxy

current_global_search = LocalProxy(lambda: current_app.extensions["global_search"])


def global_search_view_function(*args, **kwargs):
    return current_global_search.global_search_ui_resource.search(*args, **kwargs)
