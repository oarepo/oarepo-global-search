from invenio_records_resources.services.records.params import ParamInterpreter


class GlobalSearchStrParam(ParamInterpreter):
    """Evaluate the 'q' or 'suggest' parameter."""

    def apply(self, identity, search, params):
        """Evaluate the query str on the search."""
        if "json" in params:
            query = params["json"]["query"]
            aggs = params["json"]["aggs"]
            post_filter = params["json"]["post_filter"]
            for agg in aggs:
                search.aggs.bucket(agg, aggs[agg])
            search = search.query(query)
            if post_filter != {}:
                search = search.post_filter(post_filter)
            if params["json"].get("sort"):
                search = search.sort(params["json"]["sort"][0])
        return search
