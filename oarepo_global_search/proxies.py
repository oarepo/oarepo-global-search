from flask import current_app
from werkzeug.local import LocalProxy

current_global_search = LocalProxy(lambda: current_app.extensions["global_search"])
