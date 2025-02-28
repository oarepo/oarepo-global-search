from oarepo_global_search.info import GlobalSearchInfoComponent


def test_info(app, db, search_clear, identity_simple, client):
    data = {"links": {}}

    GlobalSearchInfoComponent(None).repository(data=data)

    # note - in pytest we create only the "api" application that sits directly on http://localhost/,
    # not embedded under /api, therefore the links are directly on the root.
    assert data["links"]["records"] == "http://localhost/search/"
    assert data["links"]["drafts"] == "http://localhost/user/search/"
