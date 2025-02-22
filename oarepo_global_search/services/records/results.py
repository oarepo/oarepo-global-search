from invenio_records_resources.services import LinksTemplate
from invenio_records_resources.services.records.results import (
    RecordList as BaseRecordList,
)
from collections import defaultdict


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

        # get json $schema to service mapping
        schema_to_service = {}
        for service_dict in self.services:
            for service, schema in service_dict.items():
                schema_to_service[schema] = service

        # group hits by schema and log order
        hits_by_schema = defaultdict(list)
        id_to_order: dict[str, int] = {}
        for idx, hit in enumerate(self._results):
            # log order
            id_to_order[hit.id] = idx
            hits_by_schema[hit["$schema"]].append(hit)

        # for each schema, convert the results using their result list and gather them to records variable
        records = []
        for schema, hits in hits_by_schema.items():
            service = schema_to_service[schema]
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

        # sort the records by the original order
        records.sort(key=lambda x: id_to_order[x["id"]])
        return records
