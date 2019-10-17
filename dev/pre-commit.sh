#!/bin/bash
# Add the pre commit hook e.g. by running the following command in the root project directory
#   ln -sf ../../dev/pre-commit.sh .git/hooks/pre-commit
set -eu

files_to_consider=$@
if [ -z "$files_to_consider" ]; then
    files_to_consider=$(git diff --cached --name-only --diff-filter=ACM)
else
    files_to_consider=$(echo "$files_to_consider" | tr ' ' '\n')
fi

pyfiles=$(echo "$files_to_consider" | grep -E '\.py$' | tr '\n' ' ')
if [ "$pyfiles" ]; then
    venv=$(ls -1 ~/.virtualenvs/stub-analyzer{,*}/bin/activate 2>/dev/null | head -n1)
    if [ -f "$venv" ]; then
        # Allow multiple environments
        set +u  # Ignore error: "bin/activate: line 57: PS1: unbound variable"
        . $venv
        set -u
    fi
    SILENT=1 dev/fmt.sh $pyfiles
    git add $pyfiles
fi
