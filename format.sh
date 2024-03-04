black oarepo_global_search tests --target-version py310
autoflake --in-place --remove-all-unused-imports --recursive oarepo_global_search tests
isort oarepo_global_search tests  --profile black
