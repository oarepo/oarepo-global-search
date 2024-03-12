from flask import Blueprint


def create_app_blueprint(app):
    # just to register templates
    blueprint = Blueprint("global_search_app", __name__,
                          url_prefix="/global-search",
                          template_folder="../ui/templates")
    return blueprint
