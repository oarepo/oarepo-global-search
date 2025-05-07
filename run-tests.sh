#!/bin/bash

set -e

OAREPO_VERSION=${OAREPO_VERSION:-12}
PYTHON=${PYTHON:-python3}
export PIP_EXTRA_INDEX_URL=https://gitlab.cesnet.cz/api/v4/projects/1408/packages/pypi/simple
export UV_EXTRA_INDEX_URL=https://gitlab.cesnet.cz/api/v4/projects/1408/packages/pypi/simple

if [ -d .venv-builder ] ; then
    rm -rf .venv-builder
fi

${PYTHON} -m venv .venv-builder
.venv-builder/bin/pip install -U setuptools pip wheel
.venv-builder/bin/pip install oarepo-model-builder



BUILDER=.venv-builder/bin/oarepo-compile-model


if true ; then
    test -d model-a && rm -rf model-a
    test -d model-b && rm -rf model-b
    test -d model-c && rm -rf model-c

    ${BUILDER} tests/modela.yaml --output-directory model-a -vvv
    ${BUILDER} tests/modelb.yaml --output-directory model-b -vvv
    .venv-builder/bin/pip install oarepo-model-builder-drafts
    ${BUILDER} tests/modelc.yaml --output-directory model-c -vvv
fi

if [ -d .venv-tests ] ; then
    rm -rf .venv-tests
fi


${PYTHON} -m venv .venv-tests
source .venv-tests/bin/activate

pip install -U setuptools pip wheel
pip install pyyaml opensearch-dsl
pip install "oarepo[tests,s3,rdm]==${OAREPO_VERSION}.*"
pip install oarepo-ui
pip install -e .[tests]
pip install -e model-a
pip install -e model-b
pip install -e model-c

pytest tests