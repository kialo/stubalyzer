#!/bin/bash

VIRTUALENV_NAME=stub-analyzer

rm -rf ~/.virtualenvs/$VIRTUALENV_NAME
virtualenv -p python3.7 ~/.virtualenvs/$VIRTUALENV_NAME
. ~/.virtualenvs/$VIRTUALENV_NAME/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt
pip install -e .

if [ ! -f .venv ]
then
    echo "$VIRTUALENV_NAME" > .venv
fi
