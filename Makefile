UV := uv
MAP ?= sample_map.txt
.DEFAULT_GOAL := help

.PHONY: install run visual debug clean lint lint-strict help

# Map files must be supplied as MAP=path.  Without this check, Make treats a
# positional path as another target and may silently run sample_map.txt.
ifneq ($(filter run visual debug,$(MAKECMDGOALS)),)
ifneq ($(word 2,$(MAKECMDGOALS)),)
$(error Specify a map as MAP=path/to/map.txt)
endif
endif

install:
	$(UV) sync --dev

run:
	$(UV) run python fly_in.py "$(MAP)"

visual:
	$(UV) run python fly_in.py --visual "$(MAP)"

debug:
	$(UV) run python -m pdb fly_in.py "$(MAP)"

clean:
	find . \
		-path './.git' -prune -o \
		-path './.venv' -prune -o \
		-type d -name '__pycache__' -prune -exec rm -rf {} +
	find . \
		-path './.git' -prune -o \
		-path './.venv' -prune -o \
		-type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	rm -rf .mypy_cache .pytest_cache .ruff_cache htmlcov build dist
	rm -f .coverage .coverage.*

lint:
	$(UV) run flake8 *.py
	$(UV) run mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(UV) run flake8 *.py
	$(UV) run mypy . --strict

help:
	@echo "make install          Install project and development dependencies"
	@echo "make run              Run with sample_map.txt"
	@echo "make run MAP=path     Run with the specified map"
	@echo "make visual MAP=path  Visualize the specified map"
	@echo "make debug MAP=path   Run under pdb"
	@echo "make lint             Run required flake8 and mypy checks"
	@echo "make lint-strict      Run flake8 and mypy --strict"
	@echo "make clean            Remove generated caches and build files"
