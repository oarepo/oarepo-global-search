def create_global_search(app):
    """Create requests blueprint."""
    ext = app.extensions["global_search"]
    blueprint = ext.global_search_resource.as_blueprint()
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
