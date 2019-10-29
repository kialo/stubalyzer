#!/bin/bash

# Apply autoformatting to Python files
# Usage: ./dev/fmt.sh [FILES]
#
# The behaviour can be configured using environment variables:
# SILENT: disable printing of executed commands command

set -eu
function enable_xtrace {
    [ "${SILENT:-}" ] || set -x
}
enable_xtrace

cd $(dirname $0)/..


if [ $# -eq 0 ]
then
    isort_params="--recursive stub_analyzer testing setup.py"
    black_params="stub_analyzer testing setup.py"
else
    isort_params="$@"
    black_params="$@"
fi

isort $isort_params
black $black_params
