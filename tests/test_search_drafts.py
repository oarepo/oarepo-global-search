from invenio_access.permissions import system_identity
from modelc.proxies import current_service as modelc_service
from modelc.records.api import ModelcDraft


def test_description_no_params(
    app, db, search_clear, global_search_service, custom_fields, identity_simple
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

    result_without_query = global_search_service.search_drafts(system_identity, {})

    result_with_query = global_search_service.search_drafts(
        identity_simple, {"q": "jej"}
    )

    assert len(result_with_query.to_dict()["hits"]["hits"]) == 1
    assert (
        result_with_query.to_dict()["links"]["self"]
        == "http://localhost/user/search?page=1&q=jej&size=25&sort=bestmatch"
    )
    assert (
        result_without_query.to_dict()["links"]["self"]
        == "http://localhost/user/search?page=1&size=25&sort=updated-desc"
    )


def test_description_search(
    app, db, search_clear, global_search_service, custom_fields, identity_simple
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

    result = global_search_service.search_drafts(
        identity_simple,
        {"q": "jej", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
    )
    results = result.to_dict()
    assert len(results["hits"]["hits"]) == 1

    rec_id = modelc_record2.data["id"]
    assert rec_id == results["hits"]["hits"][0]["id"]
    assert (
        results["links"]["self"]
        == "http://localhost/user/search?page=1&q=jej&size=10&sort=bestmatch"
    )
    assert (
        results["hits"]["hits"][0]["links"]["self"]
        == f"http://localhost/modelc/{rec_id}/draft"
    )


def test_search_drafts_with_disabled_services(
    app, db, search_clear, global_search_service, custom_fields, identity_simple
):
    for m in app.config['GLOBAL_SEARCH_MODELS']:
        if m['model_service'] == 'modelc.services.records.service.ModelcService':
            m['search_drafts'] = False

    try:

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

        result = global_search_service.search_drafts(
            identity_simple,
            {"q": "jej", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
        )
        results = result.to_dict()
        assert len(results["hits"]["hits"]) == 0
    
    finally:
        for m in app.config['GLOBAL_SEARCH_MODELS']:
            if m['model_service'] == 'modelc.services.records.service.ModelcService':
                del m['search_drafts']


    result = global_search_service.search_drafts(
        identity_simple,
        {"q": "jej", "sort": "bestmatch", "page": 1, "size": 10, "facets": {}},
    )
    results = result.to_dict()
    assert len(results["hits"]["hits"]) == 1
        