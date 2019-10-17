#!/bin/bash

# Apply autoformatting to Python files
# Usage: ./dev/fmt.sh [FILES]
#
# The behaviour can be configured using environment variables:
# SILENT: disable printing of executed commands command
# CHECK_FORMAT: Fail if any changes were made

set -eu
function enable_xtrace {
    [ "${SILENT:-}" ] || set -x
}
enable_xtrace

cd $(dirname $0)/..

isort "$@"
black "$@"
