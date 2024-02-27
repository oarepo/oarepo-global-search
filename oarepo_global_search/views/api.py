def create_global_search(app):
    """Create requests blueprint."""
    ext = app.extensions["global_search"]
    blueprint = ext.global_search_resource.as_blueprint()
    return blueprint


def create_global_user_search(app):
    """Create requests blueprint."""
    ext = app.extensions["global_search"]
    blueprint = ext.global_user_search_resource.as_blueprint()
    return blueprint
