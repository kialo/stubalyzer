#!/bin/bash

cd "$(dirname $0)/.."

echo "Running mypy with generated stubs"
MYPYPATH=./stubs-generated mypy test_code

echo "Running mypy with handwritten stubs"
MYPYPATH=./stubs-handwritten mypy test_code
