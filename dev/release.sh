#!/bin/bash
set -e

source "$(dirname $0)/ensure_venv.sh"
source "$(dirname $0)/util.sh"

old_version="v$(get_version)"

function changes {
    git log --abbrev-commit --format='-  %s - %h' ${old_version}..HEAD | cat
}

if [ -z "$1" ]; then
    echo "Please specify the version increment (patch, minor, major) as the first argument"
    exit 1
fi

echo "Cleaning up build and dist output..."
rm -rf build dist

echo "Bumping $1 version..."
bump2version $@

new_version="v$(get_version)"

echo ""
echo "Bumped version from $old_version to $new_version"

echo ""
if confirm "Tag new version" "Y"; then
    echo "Tagging ${new_version}..."
    cat << EOF | git tag -s ${new_version} -F-
Release ${new_version}

$(changes)
EOF
    tagged=true
else
    tagged=false
    echo "Not tagging ${new_version}."
fi

echo ""
if $tagged && confirm "Push tag ${new_version} to remote?"; then
    echo "Pushing tag ${new_version}..."
    git push origin ${new_version}
else
    echo "Not pushing tag."
fi

echo ""
if confirm "Publish ${new_version} to pypi?"; then
    echo "Publishing ${new_version} to pypi..."
    flit publish
    echo "git push origin ${new_version}"
else
    echo "Not publishing to pypi."
fi

heading="${new_version} - $(format_date)"
heading_line=$(dashes $(length "$heading"))

changelog=$(cat <<EOF
\`Commits <https://github.com/kialo/stubalyzer/compare/${new_version}...master>\`__

$heading
$heading_line

\`Commits <https://github.com/kialo/stubalyzer/compare/${old_version}...${new_version}>\`__

$(changes)
EOF
)

echo ""
tput smso
echo "Please replace the \"Commits\" link under the \"Development\" heading in CHANGELOG.rst with the following:"
echo "<<<<<<<<<<<<<<<<"
tput rmso
echo "$changelog"
tput smso
echo ">>>>>>>>>>>>>>>>"
echo "Once updated, commit the changes and push."
tput rmso
