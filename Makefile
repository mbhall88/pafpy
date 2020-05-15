PROJECT = pafpy
COVG_REPORT = htmlcov/index.html
OS := $(shell uname -s)
# MAIN #########################################################################

.PHONY: all
all: install

# DEPENDENCIES #################################################################

.PHONY: install
install:
	poetry install

# TIDY #################################################################
.PHONY: fmt
fmt: clean
	poetry run isort --apply --atomic tests/*.py $(PROJECT)/*.py
	poetry run black .

.PHONY: lint
lint: clean
	poetry run flake8 .

# BUILD ########################################################################

# TEST ########################################################################
.PHONY: test-code
test-code: clean
	poetry run pytest tests/

.PHONY: test-docs
test-docs:
	poetry run scripts/mdpydoctest -o tests/test_docs.py $(PROJECT)/

.PHONY: test
test: test-code test-docs clean

.PHONY: coverage
coverage:
	poetry run pytest --cov-report term --cov-report html --cov=$(PROJECT) --cov-branch tests/
ifeq ($(OS), Linux)
	xdg-open $(COVG_REPORT)
else ifeq ($(OS), Darwin)
	open $(COVG_REPORT)
else
	echo "ERROR: Unknown OS detected - $OS"
endif

# PRECOMMIT ########################################################################
.PHONY: precommit
precommit: fmt lint test

# CLEANUP ######################################################################
.PHONY: clean
clean:
	rm -f tests/test_docs.py