#!/bin/bash

cd $(dirname $0)/..

rm -rf ./venv
python3 -m venv venv
source ./venv/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt
pip install -e .

if [ ! -f .venv ]
then
    echo "venv" > .venv
fi
