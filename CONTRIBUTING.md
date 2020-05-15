# Contributing

Contributions are very welcome. Please ensure all of your contributions are made via a
pull request from a fork.

## Setup

The recommended development environment is through [poetry][poetry]. If you prefer to
use something else that is fine, but beware it could lead to different environment
behaviour. The [`poetry.lock`][lock] file under version control should ensure you are
setup with the exact same environment as anyone else contributing to the library. Most
of the standard development tasks are managed through a `Makefile`. The
[`Makefile`][makefile] assumes that you are using `poetry`.

After cloning your fork locally and entering to project directory, you can setup the
poetry environment with

```sh
make install
```

## Formatting

All code is formatted with `black` and `isort`. To format the project, run

```sh
make fmt
```

## Linting

Linting is done by `flake8`. Please ensure there are no warnings prior to pushing any
work.

```sh
make lint
```

## Testing

To test both the code and documentation, run

```sh
make test
```

### Code

All unit tests are contained in the `tests` directory. If you add any code, please
ensure it is tested. Tests are handled by `pytest`. To test just the code, without the
also testing the documentation, run

```sh
make test-code
```

### Docs

The document testing is orchestrated by [`scripts/mdpydoctest`][mdpydoctest]. This
script will extract all markdown python code blocks from docstrings in python files and
write a test file with a unit test for each snippet. It then runs `pytest` on this file
to ensure all code examples in the docstrings are correct. To test the docs, run

```sh
make test-docs
```

### Coverage

Please try and keep the project's code coverage as high as possible. To check the code
covergae, run

```sh
make coverage
```

This should show the coverage on the terminal and also open a HTML report in your web
browser.

## Documentation

The code is documented using markdown docstrings. The convention this project follows is
akin to that used by the Rust programming language. The beginning of the docstring
should explain what the function does and if it returns anything. This is followed,
where relevant, by an example section `## Example`. All examples should be valid,
self-contained examples that can be copied and pasted in to a python sh and executed
successfully (assuming the user has `pafpy` installed). These code snippets must be in a
code block annotated at `py` or `python`. See the code for examples. If the code being
documented can raise an exception, the type(s) of execptions should be documented in a
`## Errors` section also.

The documentation can be served locally in a browser so that you can view changes in realtime by running

```sh
make serve-docs
```

and then navigating to the URL printed in the terminal (most likely <http://localhost:8080>).

The docs can also be built by running

```sh
make docs
```
Then open `docs/index.html` to view the documentation that will be deployed on pushing to `master`.

## Committing

There is a convenience rule in the `Makefile` that can be run prior to committing that
will run most of the above tasks for you

```sh
make precommit
```

[poetry]: https://python-poetry.org/
[makefile]: https://github.com/mbhall88/pafpy/blob/master/Makefile
[lock]: https://github.com/mbhall88/pafpy/blob/master/poetry.lock
[mdpydoctest]: https://github.com/mbhall88/pafpy/blob/master/scripts/mdpydoctest

