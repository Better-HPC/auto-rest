# Install and Setup

Auto-REST is available for installation from the Python Package Index (PyPI).
Using the `pipx` package manager is strongly recommended, however the standard `pip` utility can also be used.

=== "pipx (recommended)"

    ```shell
    pipx install auto-rest-api
    ```

=== "pip (not recommended)"

    ```shell
    pip install auto-rest-api
    ```

## Adding Custom Drivers

!!! danger "Important: Driver Support"

    Database drivers are not required to support the full range of database operations.
    In some cases driver maintainers may choose not to implement certain features.
    In others, a driver may be restricted due to reasons inherent to the underlying DBMS.
    As a result, certain Auto-REST features may be unavailable if not supported by the underlying database driver.

Auto-REST includes pre-packaged drivers for most common databases.
The table below lists the supported database systems along with their default drivers.

| Database System      | Default Driver       |
|----------------------|----------------------|
| SQLite               | `sqlite+aiosqlite`   |
| PostgreSQL           | `postgresql+asyncpg` |
| MySQL                | `mysql+asyncmy`      |
| Oracle               | `oracle+oracledb`    |
| Microsoft SQL Server | `mssql+aiomysql`     |


Auto-REST also supports generic database drivers compatible with the SQLAlchemy framework.
To add a new driver, install it in the same environment as the Auto-REST utility.

=== "pipx (standalone)"

    ```shell
    pipx inject auto-rest [PACKAGE_NAME]   
    ```

=== "pip (dependency)"

    ```shell
    pip install [PACKAGE_NAME]
    ```
