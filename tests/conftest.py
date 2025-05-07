import os

import pytest
from flask_principal import Identity, Need, UserNeed
from invenio_app.factory import create_api
from oarepo_runtime.services.custom_fields.mappings import prepare_cf_indices

from oarepo_global_search.proxies import current_global_search_service

pytest_plugins = [
    "pytest_oarepo.users",
]

@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return create_api


@pytest.fixture()
def identity_simple(users):
    """Simple identity fixture."""
    return users[0].identity


@pytest.fixture()
def global_search_service():
    return current_global_search_service


@pytest.fixture(scope="module")
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["JSONSCHEMAS_HOST"] = "localhost"
    app_config["RECORDS_REFRESOLVER_CLS"] = (
        "invenio_records.resolver.InvenioRefResolver"
    )
    app_config["RECORDS_REFRESOLVER_STORE"] = (
        "invenio_jsonschemas.proxies.current_refresolver_store"
    )
    app_config["RATELIMIT_AUTHENTICATED_USER"] = "200 per second"
    app_config["SEARCH_HOSTS"] = [
        {
            "host": os.environ.get("OPENSEARCH_HOST", "localhost"),
            "port": os.environ.get("OPENSEARCH_PORT", "9200"),
        }
    ]
    app_config["GLOBAL_SEARCH_MODELS"] = [
        {
            "model_service": "modela.services.records.service.ModelaService",
            "service_config": "modela.services.records.config.ModelaServiceConfig",
        },
        {
            "model_service": "modelb.services.records.service.ModelbService",
            "service_config": "modelb.services.records.config.ModelbServiceConfig",
        },
        {
            "model_service": "modelc.services.records.service.ModelcService",
            "service_config": "modelc.services.records.config.ModelcServiceConfig",
        },
    ]
    app_config["SITE_API_URL"] = "http://localhost"

    return app_config


@pytest.fixture()
def custom_fields():
    prepare_cf_indices()
