#!/usr/bin/env bash
set -eu

coverage run -m pytest

# clean out old coverage results
rm -rf ./tests/coverage

coverage html --directory ./tests/coverage
