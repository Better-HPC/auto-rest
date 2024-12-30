---
hide:
  - navigation
---

# Contributing

Community contributions to the Auto-REST project are welcome!
To ensure

## Licensing

The Auto-REST project is licensed under the GNU General Public License (GPL) v3.
This license ensures the project remains open and accessible to everyone, allowing
users to modify, distribute, and use the software freely, as long as any derived works
are also shared under the same license.

All contributions to the project are required to fall under the same GPL v3 license.
By submitting your contributions, you agree to license your contributions under the 
same terms, ensuring the continued openness and accessibility of the project.

## Common Developer Tasks

This project uses the Poetry package manager to track project dependencies and build distributions.
Below are some common tasks you will need to perform during development.

### Running Tests

Application tests should be run regularly during development.
To run the test suite, start by installing the test dependencies.

```shell
poetry install --with tests
```
Tracking the application test coverage is an essential part of maintaining code quality. 
The `coverage` tool allows you to monitor how much of the code is being tested and identify areas that may need additional tests.
To run the tests with coverage, use the following command:

```shell
coverage run -m unittest discover
```

After running the tests, you can view the coverage report in the terminal with:

```shell
coverage report
```

### Building Docs

To build / preview the project documentation locally, install the documentation dependencies:

```shell
poetry install --with docs
```

Use `mkdocs` command to serve the documentation locally and preview it in your browser:

```shell
mkdocs serve
```

This command will automatically launch a local server where you can view and interact with the docs.
