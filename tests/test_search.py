
from invenio_access.permissions import system_identity
from modela.proxies import current_service as modela_service
from modela.records.api import ModelaRecord
from modelb.proxies import current_service as modelb_service
from modelb.records.api import ModelbRecord

from oarepo_global_search.services.records.service import GlobalSearchService


def test_description_search(app, db, search_clear, identity_simple):

    modela_record1 = modela_service.create(
        system_identity,
        {"metadata": {"title": "blah", "adescription": "kch"}},
    )
    modela_record2 = modela_service.create(
        system_identity,
        {"metadata": {"title": "aaaaa", "adescription": "jej"}},
    )
    modelb_record1 = modelb_service.create(
        system_identity,
        {"metadata": {"title": "blah", "bdescription": "blah"}},
    )
    ModelaRecord.index.refresh()
    ModelbRecord.index.refresh()

    result = GlobalSearchService().global_search(
        system_identity,
        {"q": "jej", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
    )
    results = result.to_dict()
    assert len(results["hits"]["hits"]) == 1

    assert modela_record2.data in results["hits"]["hits"]
    assert modelb_record1.data not in results["hits"]["hits"]
    assert modela_record1.data not in results["hits"]["hits"]


def test_basic_search(app, db, search_clear, identity_simple):

    modela_record1 = modela_service.create(
        system_identity,
        {"metadata": {"title": "blah", "adescription": "kch"}},
    )
    modela_record2 = modela_service.create(
        system_identity,
        {"metadata": {"title": "aaaaa", "adescription": "jej"}},
    )
    modelb_record1 = modelb_service.create(
        system_identity,
        {"metadata": {"title": "blah", "bdescription": "blah"}},
    )
    ModelaRecord.index.refresh()
    ModelbRecord.index.refresh()

    result = GlobalSearchService().global_search(
        system_identity,
        {"q": "blah", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
    )
    results = result.to_dict()

    assert len(results["hits"]["hits"]) == 2

    assert modela_record2.data not in results["hits"]["hits"]
    assert modelb_record1.data in results["hits"]["hits"]
    assert modela_record1.data in results["hits"]["hits"]


def test_links(app, db, search_clear, identity_simple):

    modelb_record1 = modelb_service.create(
        system_identity,
        {"metadata": {"title": "blah", "bdescription": "blah"}},
    )
    ModelaRecord.index.refresh()
    ModelbRecord.index.refresh()

    result = GlobalSearchService().global_search(
        system_identity,
        {"q": "blah", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
    )
    results = result.to_dict()

    assert (
        results["links"]["self"]
        == "https://127.0.0.1:5000/api/search?page=1&size=25&sort=newest"
    )
    assert results["hits"]["hits"][0]["links"]["self"].startswith(
        "https://127.0.0.1:5000/api/modelb/"
    )


def test_zero_hits(app, db, search_clear, identity_simple):
    modela_record1 = modela_service.create(
        system_identity,
        {"metadata": {"title": "blah", "adescription": "kch"}},
    )
    modela_record2 = modela_service.create(
        system_identity,
        {"metadata": {"title": "aaaaa", "adescription": "blah"}},
    )
    modelb_record1 = modelb_service.create(
        system_identity,
        {"metadata": {"title": "blah", "bdescription": "blah"}},
    )
    ModelaRecord.index.refresh()
    ModelbRecord.index.refresh()

    result = GlobalSearchService().global_search(
        system_identity,
        {"q": "jej", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
    )
    results = result.to_dict()

    assert len(results["hits"]["hits"]) == 0


def test_multiple_from_one_schema(app, db, search_clear, identity_simple):
    modela_record1 = modela_service.create(
        system_identity,
        {"metadata": {"title": "blah", "adescription": "kch"}},
    )
    modela_record2 = modela_service.create(
        system_identity,
        {"metadata": {"title": "aaaaa", "adescription": "blah"}},
    )
    modelb_record1 = modelb_service.create(
        system_identity,
        {"metadata": {"title": "kkkkkkkkk", "bdescription": "kkkkk"}},
    )
    ModelaRecord.index.refresh()
    ModelbRecord.index.refresh()

    result = GlobalSearchService().global_search(
        system_identity,
        {"q": "blah", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
    )
    results = result.to_dict()

    assert len(results["hits"]["hits"]) == 2
    assert modelb_record1.data not in results["hits"]["hits"]


def test_facets(app, db, search_clear, identity_simple):
    modela_record1 = modela_service.create(
        system_identity,
        {"metadata": {"title": "blah", "adescription": "1"}},
    )
    modela_record2 = modela_service.create(
        system_identity,
        {"metadata": {"title": "aaaaa", "adescription": "2"}},
    )
    modelb_record1 = modelb_service.create(
        system_identity,
        {"metadata": {"title": "kkkkkkkkk", "bdescription": "3"}},
    )

    ModelaRecord.index.refresh()
    ModelbRecord.index.refresh()

    result = GlobalSearchService().global_search(
        system_identity,
        {
            "q": "",
            "sort": "bestmatch",
            "page": 1,
            "size": 10,
            "facets": {"metadata_adescription": ["2"]},
        },
    )
    results = result.to_dict()
    assert len(results["hits"]["hits"]) == 1
    assert modela_record2.data in results["hits"]["hits"]
