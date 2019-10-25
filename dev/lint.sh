#!/bin/bash

cd $(dirname $0)/..

flake8 scripts stub_analyzer testing
mypy scripts stub_analyzer testing
