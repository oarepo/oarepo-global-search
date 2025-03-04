from collections import defaultdict

from invenio_records_resources.services import LinksTemplate
from invenio_records_resources.services.base.results import ServiceListResult
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

        # get json $schema to service mapping
        schema_to_service = {}
        for service in self.services:
            schema_to_service[service.record_cls.schema.value] = service

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


class GlobalSearchScanResultList(ServiceListResult):

    def __init__(self, result_lists):
        self._result_lists = result_lists

    def __iter__(self):
        """Iterator over the hits."""
        return self.hits

    @property
    def total(self):
        """Get total number of hits."""
        return None  # return value in invenio specified for scan

    @property
    def hits(self):
        for result_list in self._result_lists:
            yield from result_list.hits

    def to_dict(self):
        raise RuntimeError("Do not use to_dict() on scan results, iterate through hits instead.")