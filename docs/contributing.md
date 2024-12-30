---
hide:
  - navigation
---

# Contributing

Community contributions to the Auto-REST project are welcome!
To ensure consistency and maintainability, please review the following guidelines before submitting your contributions.

## Licensing

The Auto-REST project is licensed under the [GNU General Public License (GPL) v3](https://www.gnu.org/licenses/gpl-3.0.en.html).
This license allows users to modify, distribute, and use the software freely, as 
long as any derived works are shared under the same license.

All contributions to the project are required to fall under the same GPL v3 license.
By submitting your contributions, you agree to license your contributions under the 
same terms, ensuring the continued openness and accessibility of the project.

## Common Developer Tasks

Instructions are provided below for common tasks performed during development.

### Environment Setup

This project uses the [Poetry](https://python-poetry.org/) utility to manage project dependencies.
To create a new project environment, point poetry at the desired Python interpreter.

```shell
poetry env use python3.14
````

Poetry will automatically activate the new environment.
To confirm the current environment, use the `list` command.

```shell
poetry env list
```

From within the activated environment, install the project dependencies.

```shqll
poetry install
```

### Running Tests

All contributions are required to pass the application test suite.
To run the application tests, start by installing the test dependencies:

```shell
poetry install --with tests
```

The `coverage` tool tracks test coverage, helping to maintain code quality by identifying untested areas.
To run tests with coverage, use the following command:

```shell
coverage run -m unittest discover
coverage report
```

### Previewing Docs

To build and preview the documentation locally, start by installing the documentation dependencies:

```shell
poetry install --with docs
```

The `mkdocs` utility a static site generator that simplifies building and deploying project documentation. 
The following command will automatically compile the HTML documentation and launch it with a local server.

```shell
mkdocs serve
```
