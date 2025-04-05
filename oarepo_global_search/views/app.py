from flask import Blueprint


def create_app_blueprint(app):
    blueprint = Blueprint("global_search_app", __name__, url_prefix="/global-search")
    blueprint.record_once(init_create_api_blueprint)

    return blueprint


def init_create_api_blueprint(state):
    """Init app."""
    app = state.app

    ext = app.extensions["global_search"]

    with app.app_context():
        # register service
        sregistry = app.extensions["invenio-records-resources"].registry
        sregistry.register(
            ext.service_records, service_id=ext.service_records.config.service_id
        )
