#!/bin/bash
set -e
source "$(dirname $0)/util.sh"

function get_version {
    python -c 'print(__import__("stubalyzer").__version__)'
}

if [ -z "$1" ]; then
    echo "Please specify the version increment (patch, minor, major) as the first argument"
    exit 1
fi

echo "Cleaning up build and dist output..."
rm -rf build dist

old_version="v$(get_version)"

echo "Bumping $1 version..."
bump2version $@

new_version="v$(get_version)"

echo "Bumped version from $old_version to $new_version"
echo ""
tput smso
echo "Please update the 'Commits' link under 'Development' in CHANGELOG.rst to the following:"
echo "<<<<<<<<<<<<<<<<"
tput rmso
echo ""
echo "\`Commits <https://github.com/kialo/stubalyzer/compare/${new_version}...master>\`__"
echo ""
tput smso
echo ">>>>>>>>>>>>>>>>"
tput rmso

heading="${new_version} - $(format_date)"
heading_line=$(dashes $(length "$heading"))

tput smso
echo "Also add a new section below 'Development':"
echo "<<<<<<<<<<<<<<<<"
tput rmso
echo ""
echo "$heading"
echo "$heading_line"
echo ""
echo "\`Commits <https://github.com/kialo/stubalyzer/compare/${old_version}...${new_version}>\`__"
echo ""
git log --abbrev-commit --format='-  %s - %h' ${old_version}..HEAD | cat
echo ""
tput smso
echo ">>>>>>>>>>>>>>>>"
tput rmso

tput smso
echo "Once updated, commit the changes, tag, push and upload to PyPI:"
echo "<<<<<<<<<<<<<<<<"
tput rmso
echo ""
echo "git commit -a -m 'Update changelog'"
echo "git tag -s ${new_version}"
echo "git push"
# Is this necessary?
echo "git push --tags"
echo "python setup.py -q sdist bdist_wheel"
echo "twine upload dist/*"
echo ""
tput smso
echo ">>>>>>>>>>>>>>>>"
tput rmso
