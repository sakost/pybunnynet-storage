FORMAT_DIRS=pybunnynet_storage
TOML_FILES=poetry.lock pyproject.toml
POETRY_EXEC=poetry
PYTHON_EXEC=$(POETRY_EXEC) run python

.PHONY: install
install:
	python -m poetry install

.PHONY: pretty
pretty: isort black autoflake toml-sort

.PHONY: black
black:
	$(PYTHON_EXEC) -m black -t py310 $(FORMAT_DIRS)

.PHONY: isort
isort:
	$(PYTHON_EXEC) -m isort $(FORMAT_DIRS)

.PHONY: autoflake
autoflake:
	$(PYTHON_EXEC) -m autoflake -i -r --ignore-init-module-imports --remove-all-unused-imports --expand-star-imports $(FORMAT_DIRS)


.PHONY: toml-sort
toml-sort:
	$(POETRY_EXEC) run toml-sort $(TOML_FILES) -i -a
