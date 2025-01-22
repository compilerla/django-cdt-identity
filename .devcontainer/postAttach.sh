#!/usr/bin/env bash
set -eux

# initialize pre-commit
git config --global --add safe.directory /home/cdt/src
pre-commit install --install-hooks --overwrite
