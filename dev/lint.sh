#!/bin/bash

cd $(dirname $0)/..

flake8 stub_analyzer testing
mypy stub_analyzer testing
