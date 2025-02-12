#!/usr/bin/env bash
set -ux

# initialize pre-commit
git config --global --add safe.directory /home/cdt/src
pre-commit install --install-hooks --overwrite

# ensure the test Django app is setup
python manage.py migrate
python manage.py createsuperuser --no-input
