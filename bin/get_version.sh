#!/bin/bash

ROOT_DIR="$(dirname $(dirname $(realpath $0)))"

PYPROJECT_TOML="${ROOT_DIR}/pyproject.toml"

VERSION=$(awk -F'[ ="]+' '$1 == "version" { print $2 }' ${PYPROJECT_TOML})

printf $VERSION