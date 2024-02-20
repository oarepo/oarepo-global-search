import pytest
import time
from invenio_access.permissions import system_identity
from modela.proxies import current_service as modela_service
from modelb.proxies import current_service as modelb_service
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
    time.sleep(1)

    result = GlobalSearchService(system_identity,{'q': 'jej', 'sort': 'bestmatch', 'page': 1, 'size': 10, 'facets': {}} ).global_search()
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
    time.sleep(1)

    result = GlobalSearchService(system_identity,{'q': 'blah', 'sort': 'bestmatch', 'page': 1, 'size': 10, 'facets': {}} ).global_search()
    results = result.to_dict()

    assert len(results["hits"]["hits"]) == 2

    assert modela_record2.data not in results["hits"]["hits"]
    assert modelb_record1.data in results["hits"]["hits"]
    assert modela_record1.data in results["hits"]["hits"]


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
    time.sleep(1)

    result = GlobalSearchService(system_identity,{'q': 'jej', 'sort': 'bestmatch', 'page': 1, 'size': 10, 'facets': {}} ).global_search()
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
    time.sleep(1)

    result = GlobalSearchService(system_identity,{'q': 'blah', 'sort': 'bestmatch', 'page': 1, 'size': 10, 'facets': {}} ).global_search()
    results = result.to_dict()

    assert len(results["hits"]["hits"]) == 2
    assert modelb_record1.data not in results["hits"]["hits"]

def test_common_facet(app, db, search_clear,es_clear, identity_simple):
    modela_record1 = modela_service.create(
        system_identity,
        {"metadata": {"title": "blah", "adescription": "k"}},
    )
    modela_record2 = modela_service.create(
        system_identity,
        {"metadata": {"title": "aaaaa", "adescription": "j"}},
    )
    modelb_record1 = modelb_service.create(
        system_identity,
        {"metadata": {"title": "kkkkkkkkk", "bdescription": "kkkkk"}},
    )
    time.sleep(5)

    result = GlobalSearchService(system_identity, {'q': '', 'sort': 'bestmatch', 'page': 1, 'size': 10,  'facets': {"metadata_adescription": ["k"]}}).global_search()
    results = result.to_dict()
    assert len(results["hits"]["hits"]) == 1
    assert modela_record1.data in results["hits"]["hits"]

