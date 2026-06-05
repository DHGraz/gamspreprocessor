# make test, coverage, documentation, etc
SHELL := /bin/bash

.PHONY: all test coverage clean test-all build

all: test lint build

test:
	@uv run pytest tests 

# Run all tests with different python versions
test-versions:
	@uv run --python 3.11 --isolated --with-editable '.[test]' pytest
	@uv run --python 3.12 --isolated --with-editable '.[test]' pytest
	@uv run --python 3.13 --isolated --with-editable '.[test]' pytest
# 3.14 depencies currently have some wheel issues
	# @uv run --python 3.14 --isolated --with-editable '.[test]' pytest

coverage:
	@uv run pytest tests --cov-report term-missing --cov=gamspreprocessor 
	

lint:
	@uv run ruff check src

# buuild documentation into dist-docs folder
docs-de:
	@uv run zensical serve --config-file docs/de/zensical.toml

# serve documentation at localhost:8000
docs-en:
	@uv run mkdocs serve -o -f docs/en/mkdocs.yml --dev-addr 0.0.0.0:8000

build:
	@uv build	