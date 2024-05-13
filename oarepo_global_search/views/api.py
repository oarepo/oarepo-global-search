def create_global_search(app):
    """Create requests blueprint."""
    ext = app.extensions["global_search"]
    blueprint = ext.global_search_resource.as_blueprint()
    return blueprint


def create_global_user_search(app):
    """Create requests blueprint."""
    ext = app.extensions["global_search"]
    blueprint = ext.global_user_search_resource.as_blueprint()
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

        # Register indexer
        if hasattr(ext.service_records, "indexer"):
            iregistry = app.extensions["invenio-indexer"].registry
            iregistry.register(
                ext.service_records.indexer,
                indexer_id=ext.service_records.config.service_id,
            )
