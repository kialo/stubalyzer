#!/bin/bash
# Source this script
if [[ -z $VIRTUAL_ENV ]]; then
    python3 -m venv ./venv
    source ./venv/bin/activate
fi
