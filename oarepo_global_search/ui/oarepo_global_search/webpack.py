from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    ".",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={"oarepo_global_search": "./js/oarepo_global_search/search"},
            dependencies={},
            devDependencies={},
            aliases={},
        )
    },
)
