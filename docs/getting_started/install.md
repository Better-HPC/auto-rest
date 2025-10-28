# Install and Setup

The Auto-REST package is published on PyPI.
Installation via `pipx` is recommended, though the `pip` utility can also be used.

=== "pipx (standalone)"

    ```shell
    pipx install auto-rest-api
    ```

=== "pip (dependency)"

    ```shell
    pip install auto-rest-api
    ```

## Adding Custom Drivers

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

!!! danger "Important: Driver Support"

    SQLAlchemy does not enforce minimum feature requirements for database drivers
    Some drivers may omit functionality or expose limitations inherent to the underlying DBMS.
    As a result, specific Auto-REST features may be unavailable when unsupported by the selected driver.
    
=== "pipx (standalone)"

    ```shell
    pipx inject auto-rest [PACKAGE_NAME]   
    ```

=== "pip (dependency)"

    ```shell
    pip install [PACKAGE_NAME]
    ```
