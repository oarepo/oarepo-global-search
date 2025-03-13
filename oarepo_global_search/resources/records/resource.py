from flask import g
from flask_resources import (
    request_body_parser,
    resource_requestctx,
    response_handler,
    route,
)
from flask_resources.resources import Resource
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.resource import request_search_args

from oarepo_global_search.services.records.service import GlobalSearchService

request_json_search_args = request_body_parser()


class GlobalSearchResource(Resource, ErrorHandlersMixin):
    def __init__(self, config, service: GlobalSearchService):
        super().__init__(config)
        self.service = service

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        url_rules = [
            route("GET", routes["list"], self.search),
            route("POST", routes["list"], self.json_search),
            route("GET", routes["user-list"], self.search_user),
            route("POST", routes["user-list"], self.json_search_user),
            route("GET", routes["all-list"], self.search_all_records),
        ]
        return url_rules

    @request_search_args
    @response_handler(many=True)
    def search(self):
        items = self.service.search(g.identity, params=resource_requestctx.args)
        return items.to_dict(), 200

    @request_search_args
    @request_json_search_args
    @response_handler(many=True)
    def json_search(self):
        items = self.service.search(
            g.identity,
            params={
                **resource_requestctx.args,
                "advanced_query": resource_requestctx.data,
            },
        )
        return items.to_dict(), 200

    @request_search_args
    @response_handler(many=True)
    def search_user(self):
        items = self.service.search_drafts(g.identity, params=resource_requestctx.args)
        return items.to_dict(), 200

    @request_search_args
    @request_json_search_args
    @response_handler(many=True)
    def json_search_user(self):
        items = self.service.search_drafts(
            g.identity,
            params={
                **resource_requestctx.args,
                "advanced_query": resource_requestctx.data,
            },
        )
        return items.to_dict(), 200

    @request_search_args
    @response_handler(many=True)
    def search_all_records(self):
        items = self.service.search_all_records(g.identity, params=resource_requestctx.args)
        return items.to_dict(), 200

