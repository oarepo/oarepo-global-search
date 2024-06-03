import copy
import json

from flask import Response, make_response
from flask_resources import ResponseHandler


class GlobalSearchResponseHandler(ResponseHandler):

    def __init__(self, serializers, headers=None):
        """Constructor."""
        self.serializers = serializers
        self.headers = headers

    def make_response(self, obj_or_list, code, many=False):
        """Builds a response for one object."""
        # If view returns a response, bypass the serialization.
        if isinstance(obj_or_list, Response):
            return obj_or_list

        serialized_hits = []
        for hit in obj_or_list["hits"]["hits"]:
            for serializer in self.serializers:
                if serializer["schema"] == hit["$schema"]:
                    outcome = serializer["serializer"].serialize_object(hit)
                    serialized_hits.append(json.loads(outcome))

        serialized = copy.deepcopy(obj_or_list)
        serialized["hits"]["hits"] = serialized_hits

        return make_response(
            "" if obj_or_list is None else serialized,
            code,
            self.make_headers(obj_or_list, code, many=many),
        )
