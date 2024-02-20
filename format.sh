black oarepo_model_builder_relations tests --target-version py310
autoflake --in-place --remove-all-unused-imports --recursive oarepo_model_builder_relations tests
isort oarepo_model_builder_relations tests  --profile black
