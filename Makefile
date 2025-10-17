# make test, coverage, documentation, etc
SHELL := /bin/bash

.PHONY: all test coverage clean test-all build

all: test coverage lint build
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

build:
	@uv build	