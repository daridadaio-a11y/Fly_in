UV := uv
MAP ?= sample_map.txt

.PHONY: install run debug clean lint lint-strict test help

install:
	$(UV) sync --dev

run:
	$(UV) run python fly_in.py $(MAP)

visual:
	$(UV) run python fly_in.py --visual $(MAP)

debug:
	$(UV) run python -m pdb fly_in.py $(MAP)

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	rm -rf .mypy_cache .pytest_cache .ruff_cache htmlcov build dist
	rm -f .coverage .coverage.*

lint:
	$(UV) run flake8 *.py tests
	$(UV) run mypy *.py tests \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(UV) run flake8 *.py tests
	$(UV) run mypy *.py tests --strict

test:
	$(UV) run pytest -q

help:
	@echo "make install          Install project and development dependencies"
	@echo "make run              Run with sample_map.txt"
	@echo "make run MAP=path     Run with the specified map"
	@echo "make debug MAP=path   Run under pdb"
	@echo "make lint             Run required flake8 and mypy checks"
	@echo "make lint-strict      Run flake8 and mypy --strict"
	@echo "make test             Run the test suite"
	@echo "make clean            Remove generated caches and build files"
