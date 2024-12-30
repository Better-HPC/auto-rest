# Install and Setup

Auto-REST is built in Python and can be installed directly from the Python Package Index (PyPI).
The `pipx` package manager is recommended for standalone installations, which isolates the package in its own environment.
Alternatively, the standard `pip` utility can be used to install Auto-REST as a dependency within an existing project.

=== "pipx (standalone)"

    ```bash
    pipx install auto-rest
    ```

=== "pip (dependency)"

    ```bash
    pip install auto-rest
    ```

## Adding Custom Drivers

Auto-REST includes drivers for most common database systems by default.
However, additional drivers can be installed to support other database types or as alternatives to the prepackaged drivers.
Auto-REST supports any driver compatible with the SQLAlchemy Python framework, including synchronous and asynchronous drivers.

To add a new driver, install the driver package into the same environment where Auto-REST is installed.

=== "pipx (standalone)"

    ```bash
    pipx inject auto-rest [PACKAGE NAME]   
    ```

=== "pip (dependency)"

    ```bash
    pip install [PACKAGE NAME]
    ```