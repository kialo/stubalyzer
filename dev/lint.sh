#!/bin/bash

cd $(dirname $0)/..

flake8 stubalyzer testing
mypy stubalyzer testing
