from flask import current_app
from werkzeug.local import LocalProxy

current_global_search = LocalProxy(lambda: current_app.extensions["global_search"])
current_global_search_service = LocalProxy(
    lambda: current_app.extensions["global_search_service"]
)


def global_search_view_function(*args, **kwargs):
    # this function is called by the invenio_search_ui if user goes to
    # /search url (without the tailing slash). We can not use the request
    # context here as it seems not to be initialized yet. That's why
    # we just redirect to global search url (/search/) and let flask
    # handle the rest.
    import flask

    return flask.redirect("/search/")
