# MAIN #########################################################################

.PHONY: all
all: install

# DEPENDENCIES #################################################################

.PHONY: install
install:
	poetry install

# TIDY #################################################################
.PHONY: fmt
fmt:
	poetry run isort --apply --atomic tests/*.py pafpy/*.py
	poetry run black .

.PHONY: lint
lint:
	poetry run flake8 .

# BUILD ########################################################################

# TEST ########################################################################
.PHONY: test-code
test-code:
	poetry run pytest tests/

.PHONY: test-docs
test-docs:
	poetry run scripts/mkpydoctest -o tests/test_docs.py pafpy/

.PHONY: test
test: test-code test-docs

.PHONY: coverage
coverage:
	poetry run pytest --cov-report term --cov-report html --cov=pafpy --cov-branch tests/
	firefox htmlcov/index.html &

# PRECOMMIT ########################################################################
.PHONY: precommit
precommit: fmt lint test

# CLEANUP ######################################################################
