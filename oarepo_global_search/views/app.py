from flask import Blueprint


def create_app_blueprint(app):
    blueprint = Blueprint("global_search_app", __name__, url_prefix="/global-search")
    return blueprint
