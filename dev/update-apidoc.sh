#!/bin/bash

cd $(dirname $0)/..
sphinx-apidoc -o docs/api -e -f stubalyzer '*_test.py' '**/conftest.py'
