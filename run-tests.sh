#!/bin/bash

set -e

OAREPO_VERSION=${OAREPO_VERSION:-11}

if [ -d .venv-builder ] ; then
    rm -rf .venv-builder
fi

python3 -m venv .venv-builder
.venv-builder/bin/pip install -U setuptools pip wheel
.venv-builder/bin/pip install oarepo-model-builder



BUILDER=.venv-builder/bin/oarepo-compile-model


if true ; then
    test -d model-a && rm -rf model-a
    test -d model-b && rm -rf model-b
    ${BUILDER} tests/modela.yaml --output-directory model-a -vvv
    ${BUILDER} tests/modelb.yaml --output-directory model-b -vvv
fi

if [ -d .venv-tests ] ; then
    rm -rf .venv-tests
fi


python3 -m venv .venv-tests
source .venv-tests/bin/activate

pip install -U setuptools pip wheel
pip install pyyaml opensearch-dsl
pip install "oarepo[tests]==${OAREPO_VERSION}.*"
pip install oarepo-ui
pip install -e .
pip install -e model-a
pip install -e model-b

pytest tests