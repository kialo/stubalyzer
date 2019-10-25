#!/bin/bash

cd $(dirname $0)/..
sphinx-apidoc -o docs/api -e -f stub_analyzer '*_test.py' '**/conftest.py'
