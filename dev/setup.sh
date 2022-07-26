#!/bin/bash

source "$(dirname $0)/ensure_venv.sh"
cd $(dirname $0)/..

pip install --upgrade pip wheel setuptools flit
flit install --deps all
