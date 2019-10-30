#!/bin/bash

VIRTUALENV_NAME=stubalyzer

rm -rf ~/.virtualenvs/$VIRTUALENV_NAME
virtualenv -p python3.7 ~/.virtualenvs/$VIRTUALENV_NAME
. ~/.virtualenvs/$VIRTUALENV_NAME/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt
# To install mypy 0.750+dev (which has a newer but also broken version of stubgen) uncomment this line
# pip install -U git+https://github.com/python/mypy.git#egg=mypy
pip install -e .

if [ ! -f .venv ]
then
    echo "$VIRTUALENV_NAME" > .venv
fi
