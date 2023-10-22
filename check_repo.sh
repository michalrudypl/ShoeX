#!/bin/bash

# Stop the script if any command returns an error
set -e

echo "Running black..."
black src

echo "Running isort..."
isort src

echo "Running flake8..."
flake8 src

echo "Running pylint..."
pylint src

echo "Running mypy..."
mypy src


