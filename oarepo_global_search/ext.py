
class OARepoGlobalSearch(object):
    """OARepo DOI extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["global_search"] = self

    def init_config(self, app):
        pass
    #
    # @cached_property
    # def service_records(self):
    #     return config.MODELA_RECORD_SERVICE_CLASS(
    #         config=config.MODELA_RECORD_SERVICE_CONFIG(),
    #     )