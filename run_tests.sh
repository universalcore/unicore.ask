#!/bin/bash
set -e

flake8 unicore --exclude alembic
py.test --verbose --cov ./unicore/ask unicore/ask
