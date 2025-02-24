
def indices(self):
    indices = []
    for service_dict in self.service_mapping:
        service = list(service_dict.keys())[0]
        indices.append(service.record_cls.index.search_alias)
        # if current_action.get("search") == "search_drafts" and getattr( # todo by default we search drafts too and there are other ways to eventually omit them than on index level?
        if getattr(service, "draft_cls", None):
            indices.append(service.draft_cls.index.search_alias)
    return indices

def _search_opts_from_search_obj(self, search):
    facets = {}
    sort_options = {}

    facets.update(search.facets)
    try:
        sort_options.update(search.sort_options)
    except:
        pass
    sort_default = search.sort_default
    sort_default_no_query = search.sort_default_no_query
    facet_groups = search.facet_groups
    return {
        "facets": facets,
        "facet_groups": facet_groups,
        "sort_options": sort_options,
        "sort_default": sort_default,
        "sort_default_no_query": sort_default_no_query,
    }

def _search_opts(self, config_field):
    ret = {}
    for service_dict in self.service_mapping:
        service = list(service_dict.keys())[0]
        if hasattr(service.config, config_field):
            ret = always_merger.merge(ret, self._search_opts_from_search_obj(getattr(service.config, config_field)))
    return ret

def fill_search_opts(self, search_opts_cls, search_opts):
    search_opts_cls.facets = search_opts["facets"]
    search_opts_cls.facet_groups = search_opts["facet_groups"]
    search_opts_cls.sort_options = search_opts["sort_options"]
    search_opts_cls.sort_default = search_opts["sort_default"]
    search_opts_cls.sort_default_no_query = search_opts["sort_default_no_query"]
    return search_opts_cls

@property
def indexer(self):
    return None

@property
def service_mapping(self):
    service_mapping = []
    if has_app_context() and hasattr(current_app, "config"):
        for model in current_app.config.get("GLOBAL_SEARCH_MODELS", []):
            service_def = obj_or_import_string(model["model_service"])
            service_cfg = obj_or_import_string(model["service_config"])
            service = service_def(service_cfg())
            service_mapping.append({service: service.record_cls.schema.value})

    return service_mapping

class GlobalSearchServiceConfig(PermissionsPresetsConfigMixin, InvenioRecordServiceConfig):
    """
    stored_config = current_config.get(None)
    if stored_config:
        return stored_config
    """

    base_permission_policy_cls = GlobalSearchPermissionPolicy
    PERMISSIONS_PRESETS = ["everyone"]
    result_list_cls = GlobalSearchResultList


    GlobalSearchRecord.index = IndexField(self.indices())
    GlobalSearchResultList.services = self.service_mapping
    search_opts = self._search_opts("search")
    drafts_search_opts = self._search_opts("search_drafts")

    record_cls = GlobalSearchRecord
    links_search = links_search,
    links_search_drafts = links_search_drafts,
    search = self.fill_search_opts(GlobalSearchOptions, search_opts),
    search_drafts = self.fill_search_opts(GlobalSearchDraftsOptions, drafts_search_opts),
    links_search = pagination_links("{+api}/search{?args*}")
    links_search_drafts = pagination_links("{+api}/user/search{?args*}")



    config_class = type(
        "GlobalSearchServiceConfig",
        (PermissionsPresetsConfigMixin, InvenioRecordServiceConfig),
        {
            "PERMISSIONS_PRESETS": ["everyone"],
            "base_permission_policy_cls": GlobalSearchPermissionPolicy,
            "result_list_cls": GlobalSearchResultList,
            "record_cls": GlobalSearchRecord,
            # "url_prefix": url_prefix,
            "links_search": links_search,
            "links_search_drafts": links_search_drafts,
            "search": self.fill_search_opts(GlobalSearchOptions, search_opts),
            "search_drafts": self.fill_search_opts(GlobalSearchDraftsOptions, drafts_search_opts),
        },
    )
