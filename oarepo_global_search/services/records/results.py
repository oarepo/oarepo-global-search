from invenio_records_resources.services import LinksTemplate
from invenio_records_resources.services.records.results import (
    RecordList as BaseRecordList,
)


class GlobalSearchResultList(BaseRecordList):
    services = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def aggregations(self):
        """Get the search result aggregations."""
        # TODO: have a way to label or not label
        try:
            return self._results.labelled_facets.to_dict()
        except AttributeError:
            return None

    @property
    def hits(self):
        """Iterator over the hits."""
        records = []
        hits_array = []
        order = []
        for hit in self._results:
            # log order
            order.append(hit.id)

            for service_dict in self.services:
                for service, schema in service_dict.items():
                    if hit["$schema"] == schema:
                        schema_exists = False
                        for s in hits_array:
                            if schema in s:
                                s[schema].append(hit)
                                schema_exists = True
                        if not schema_exists:
                            hits_array.append({schema: [hit]})
        for hit_dict in hits_array:
            schema = list(hit_dict.keys())[0]
            hits = hit_dict[schema]
            for s in self.services:
                sc = next(iter(s.values()))
                if sc == schema:
                    service = list(s.keys())[0]

            results = service.result_list(
                service,
                self._identity,
                hits,
                self._params,
                links_tpl=LinksTemplate(
                    service.config.links_search, context={"args": self._params}
                ),
                links_item_tpl=service.links_item_tpl,
                expandable_fields=service.expandable_fields,
                expand=self._expand,
            )
            records.extend(list(results))

        sorted_hits = sorted(records, key=lambda x: order.index(x["id"]))

        for hit in sorted_hits:
            yield hit
