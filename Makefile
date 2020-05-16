PROJECT = pafpy
COVG_REPORT = htmlcov/index.html
DOCS_DIR = docs/
DOCS_TEMPLATE = docs/templates/
OS := $(shell uname -s)
VERSION := $(shell poetry version | grep -P '(?P<version>\d.\d.\d)' --only-matching)
BOLD := $(shell tput bold)
NORMAL := $(shell tput sgr0)
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
	poetry run isort --apply tests/*.py $(PROJECT)/*.py
	poetry run black .

.PHONY: lint
lint: clean
	poetry run flake8 .

.PHONY: check-fmt
check-fmt:
	poetry run isort --check-only tests/*.py $(PROJECT)/*.py
	poetry run black --check .

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

.PHONY: test-ci
test-ci:
	poetry run pytest --cov=$(PROJECT) --cov-report=xml --cov-branch tests/

# PRECOMMIT ########################################################################
.PHONY: precommit
precommit: fmt lint test clean

# DOCS ########################################################################
.PHONY: build-docs
build-docs:
	poetry run pdoc --template-dir $(DOCS_TEMPLATE) \
	  --html --force --output-dir $(DOCS_DIR) $(PROJECT) && \
	mv $(DOCS_DIR)/$(PROJECT)/* $(DOCS_DIR)/

.PHONY: docs
docs: build-docs clean

.PHONY: serve-docs
serve-docs:
	poetry run pdoc --template-dir $(DOCS_TEMPLATE) --http : $(PROJECT)

# CLEANUP ######################################################################
.PHONY: clean
clean:
	rm -rf tests/test_docs.py $(DOCS_DIR)/$(PROJECT)/

# BUILD ########################################################################
.PHONY: build
build:
	poetry build

# TAG ########################################################################
# prints out the commands to run to tag the release and push it
.PHONY: tag
tag:
	@echo "Run $(BOLD)git tag -a $(VERSION) -m <message>$(NORMAL) to tag the release"
	@echo "Then run $(BOLD)git push origin $(VERSION)$(NORMAL) to push the tag"