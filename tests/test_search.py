from invenio_access.permissions import system_identity
from modela.proxies import current_service as modela_service
from modela.records.api import ModelaRecord
from modelb.proxies import current_service as modelb_service
from modelb.records.api import ModelbRecord
from modelc.proxies import current_service as modelc_service
from modelc.records.api import ModelcDraft


def test_description_no_params(
    app, db, global_search_service, search_clear, custom_fields, identity_simple
):
    modelc_record0 = modelc_service.create(
        system_identity,
        {"metadata": {"title": "blah", "bdescription": "bbb"}},
    )
    modelc_record1 = modelc_service.create(
        identity_simple,
        {"metadata": {"title": "blah", "bdescription": "kch"}},
    )
    modelc_record2 = modelc_service.create(
        identity_simple,
        {"metadata": {"title": "aaaaa", "bdescription": "jej"}},
    )
    ModelcDraft.index.refresh()

    result = global_search_service.search(system_identity, {"q": "jej"})
    results = result.to_dict()
    assert len(results["hits"]["hits"]) == 1
    assert (
        results["links"]["self"]
        == "http://localhost/search?page=1&q=jej&size=25&sort=bestmatch"
    )


def test_description_search(
    app, db, search_clear, global_search_service, identity_simple
):
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

    result = global_search_service.search(
        system_identity,
        {"q": "jej", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
    )
    results = result.to_dict()
    assert len(results["hits"]["hits"]) == 1

    assert modela_record2.data in results["hits"]["hits"]
    assert modelb_record1.data not in results["hits"]["hits"]
    assert modela_record1.data not in results["hits"]["hits"]


def test_basic_search(app, db, global_search_service, search_clear, identity_simple):
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

    result = global_search_service.search(
        system_identity,
        {"q": "blah", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
    )
    results = result.to_dict()

    assert len(results["hits"]["hits"]) == 2

    assert modela_record2.data not in results["hits"]["hits"]
    assert modelb_record1.data in results["hits"]["hits"]
    assert modela_record1.data in results["hits"]["hits"]


def test_links(app, db, global_search_service, search_clear, identity_simple):
    modelb_record1 = modelb_service.create(
        system_identity,
        {"metadata": {"title": "blah", "bdescription": "blah"}},
    )
    ModelaRecord.index.refresh()
    ModelbRecord.index.refresh()

    result = global_search_service.search(
        system_identity,
        {"q": "blah", "sort": "bestmatch", "page": 1, "size": 20, "facets": {}},
    )
    results = result.to_dict()

    assert (
        results["links"]["self"]
        == "http://localhost/search?page=1&q=blah&size=20&sort=bestmatch"
    )
    assert results["hits"]["hits"][0]["links"]["self"].startswith(
        "http://localhost/modelb/"
    )


def test_second_page(app, db, global_search_service, search_clear, identity_simple):
    for r in range(10):
        modelb_service.create(
            system_identity,
            {"metadata": {"title": f"blah {r}", "bdescription": "blah"}},
        )
    ModelbRecord.index.refresh()

    result = global_search_service.search(
        system_identity,
        {"q": "blah", "sort": "bestmatch", "page": 1, "size": 5, "facets": {}},
    )
    results = result.to_dict()

    assert (
        results["links"]["self"]
        == "http://localhost/search?page=1&q=blah&size=5&sort=bestmatch"
    )
    assert (
        results["links"]["next"]
        == "http://localhost/search?page=2&q=blah&size=5&sort=bestmatch"
    )

    result = global_search_service.search(
        system_identity,
        {"q": "blah", "sort": "bestmatch", "page": 2, "size": 5, "facets": {}},
    )
    results = result.to_dict()

    assert (
        results["links"]["self"]
        == "http://localhost/search?page=2&q=blah&size=5&sort=bestmatch"
    )
    assert (
        results["links"]["prev"]
        == "http://localhost/search?page=1&q=blah&size=5&sort=bestmatch"
    )


def test_zero_hits(app, db, global_search_service, search_clear, identity_simple):
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

    result = global_search_service.search(
        system_identity,
        {"q": "jej", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
    )
    results = result.to_dict()

    assert len(results["hits"]["hits"]) == 0


def test_multiple_from_one_schema(
    app, db, global_search_service, search_clear, identity_simple
):
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

    result = global_search_service.search(
        system_identity,
        {"q": "blah", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
    )
    results = result.to_dict()

    assert len(results["hits"]["hits"]) == 2
    assert modelb_record1.data not in results["hits"]["hits"]


def test_facets(app, db, global_search_service, search_clear, identity_simple):
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

    result = global_search_service.search(
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


def test_scan(app, db, global_search_service, search_clear, identity_simple):
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

    result = global_search_service.scan(system_identity)
    results = list(result.hits)
    assert len(results) == 3
