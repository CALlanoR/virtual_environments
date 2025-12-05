BIN=venv/bin/
SHELL=/bin/bash

venv: venv/bin/activate
venv/bin/activate: requirements.txt
	test -d venv || virtualenv -p /usr/bin/python3.12 venv
	venv/bin/python -m pip install --upgrade pip
	venv/bin/pip install -Ur requirements.txt
	touch venv/bin/activate

clean:
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete

lint:
	$(BIN)ruff check .
	$(BIN)ruff format --check .

format:
	$(BIN)ruff format .
	$(BIN)ruff check --fix .

test:
	$(BIN)pytest

test-cov:
	$(BIN)pytest --cov=. --cov-report=html

.PHONY: clean lint format test test-cov