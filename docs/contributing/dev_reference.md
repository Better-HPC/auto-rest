# Developer Reference

Instructions are provided below for common developer tasks.
All commands are assumed to be run from within the root project directory.

## Environment Setup

Auto-REST uses the [Poetry](https://python-poetry.org/) utility to manage project dependencies.
To create a new project environment, point poetry at the desired Python interpreter.

```shell
poetry env use python3.14
```

Poetry will automatically build and activate the new environment.
To confirm the current environment, use the `list` command.

```shell
poetry env list
```

From within the activated environment, install the project dependencies.
Using the `--all-groups` flag includes optional development dependencies in the installation.

```shell
poetry install --all-groups
```

## Running Tests

All contributions are required to pass the application test suite.
To run the tests, start by installing the test dependencies:

```shell
poetry install --with tests
```

The `coverage` tool is used to track application test coverage.
To run tests with coverage, use the following commands:

```shell
coverage run -m unittest discover
coverage report
```



## Previewing Docs

To build and preview the documentation locally, start by installing the documentation dependencies:

```shell
poetry install --with docs
```

The `mkdocs` utility a static site generator that simplifies building and deploying project documentation. 
Running the following command will automatically compile the HTML documentation and launch it with a local server.

```shell
mkdocs serve
```
