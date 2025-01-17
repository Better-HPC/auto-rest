# Install and Setup

Auto-REST is available for installation from the Python Package Index (PyPI).
Using the `pipx` package manager is strongly recommended, however the standard `pip` utility can also be used.

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


Auto-REST also supports any database driver compatible with the SQLAlchemy Python framework.
To add a new driver, install it in the same environment as the Auto-REST utility.

=== "pipx (standalone)"

    ```shell
    pipx inject auto-rest [PACKAGE_NAME]   
    ```

=== "pip (dependency)"

    ```shell
    pip install [PACKAGE_NAME]
    ```
