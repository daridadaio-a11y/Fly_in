PYTHON := .venv/bin/python
UV := uv
MAP ?= sample_map.txt

.PHONY: install run debug clean lint lint-strict test help

install:
	$(UV) sync --dev

run:
	$(PYTHON) fly_in.py $(MAP)

debug:
	$(PYTHON) -m pdb fly_in.py $(MAP)

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	rm -rf .mypy_cache .pytest_cache .ruff_cache htmlcov build dist
	rm -f .coverage .coverage.*

lint:
	$(PYTHON) -m flake8 . --exclude=.venv,__pycache__,.git,ゴミ,tmp
	$(PYTHON) -m mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--exclude '(^|/)(.venv|ゴミ|tmp)/'

lint-strict:
	$(PYTHON) -m flake8 . --exclude=.venv,__pycache__,.git,ゴミ,tmp
	$(PYTHON) -m mypy . --strict --exclude '(^|/)(.venv|ゴミ|tmp)/'

test:
	$(PYTHON) -m pytest -q

help:
	@echo "make install          Install project and development dependencies"
	@echo "make run              Run with sample_map.txt"
	@echo "make run MAP=path     Run with the specified map"
	@echo "make debug MAP=path   Run under pdb"
	@echo "make lint             Run required flake8 and mypy checks"
	@echo "make lint-strict      Run flake8 and mypy --strict"
	@echo "make test             Run the test suite"
	@echo "make clean            Remove generated caches and build files"
