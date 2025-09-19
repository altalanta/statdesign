.PHONY: env test cov badge docs serve build clean

env:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

test:
	. .venv/bin/activate || true; pytest

cov:
	. .venv/bin/activate || true; pytest --cov=statdesign --cov-report=xml --cov-report=term-missing

badge:
	. .venv/bin/activate || true; coverage-badge -o docs/coverage.svg -f

docs:
	. .venv/bin/activate || true; mkdocs build

serve:
	. .venv/bin/activate || true; mkdocs serve -a 0.0.0.0:8000

build:
	python -m build

clean:
	rm -rf .venv dist build .pytest_cache .coverage htmlcov site
