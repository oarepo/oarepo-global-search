# Global search plugin

### Usage

To use the library you need to define the following paths in the config:

```
GLOBAL_SEARCH_MODELS = [{"model_service": "documents.services.records.service.DocumentsService",
                         "service_config": "documents.services.records.config.DocumentsServiceConfig",
                         "ui_resource_config": "ui.documents.DocumentsResourceConfig",
                         "api_resource_config": "documents.resources.records.config.DocumentsResourceConfig",
                         }]
```


for example:
```
GLOBAL_SEARCH_MODELS = [{"model_service": "path_to_service_class",
                         "service_config": "path_to_service_config",
                         "ui_resource_config": "path_to_ui_resource_config",
                         "api_resource_config": "path_to_api_resource_config",
                         }]
```