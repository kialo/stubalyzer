#!/bin/bash

cd $(dirname $0)/..

flake8 stubalyzer testing
# Keep exclude list in sync with /.circleci/config.yml
# Note that we can't put this in /testing/mypy.ini because the stubs need to be found for the tests
mypy stubalyzer testing --exclude 'testing/(stubs-generated|test-stubs/test_compile_error_invalid_syntax|test-stubs/test_include_private/attr|stubs-handwritten)'
