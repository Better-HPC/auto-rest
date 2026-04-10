# Install and Setup

Hosting for the Auto-REST package is provided by [PyPI.org](https://pypi.org/project/auto-rest-api/).
Install commands are provided below for a handful of popular Python package managers.

=== "pip"

    ```shell
    pip install auto-rest-api
    ```

=== "pipx"

    ```shell
    pipx install auto-rest-api
    ```

=== "uv"

    ```shell
    uv tool install auto-rest-api
    ```

## Adding Custom Drivers

Auto-REST includes pre-packaged drivers for most common databases.
Default drivers and their corresponding database systems are listed in the table below.

| Database System      | Default Driver       |
|----------------------|----------------------|
| SQLite               | `sqlite+aiosqlite`   |
| PostgreSQL           | `postgresql+asyncpg` |
| MySQL                | `mysql+aiomysql`     |
| Oracle               | `oracle+oracledb`    |
| Microsoft SQL Server | `mssql+mssqlpython`  |

Auto-REST is designed to support any database driver compatible with the SQLAlchemy framework.
To add support for a new driver, install it in the same environment as the Auto-REST utility.

!!! danger "Important: Driver Support"

    SQLAlchemy does not enforce minimum feature requirements for database drivers.
    Some drivers may omit functionality or expose limitations inherent to the underlying database.
    As a result, specific Auto-REST features may be unavailable when unsupported by the selected driver.

=== "pip"

    ```shell
    pip install [DRIVER_PACKAGE_NAME]
    ```

=== "pipx"

    ```shell
    pipx inject auto-rest [DRIVER_PACKAGE_NAME]   
    ```

=== "uv"

    ```shell
    uv tool inject auto-rest-api [DRIVER_PACKAGE_NAME]
    ```
