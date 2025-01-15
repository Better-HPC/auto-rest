# Deploying an API

The following instructions provide a general introduction to the `auto-rest` command.
For a full list of available options, see the application help text (`auto-rest --help`).

## Launching an API

Deploying an API server requires specifying the database type and connection settings.
Using the provided arguments, `auto-rest` will automatically connect to the database,
map the database schema, and deploy a customized API server.
The API server is deployed on port `8081` by default, but can be modified via commandline arguments.

!!! example "Example: Launching an API"

    === "SQLite"
    
        The `--sqlite` flag enables support for SQLite.
        Unlike traditional database systems, SQLite is file based and requires fewer conenction settings.
        The file path to the database should be specified using the `--db-name` option.
    
        ```bash
        auto-rest --sqlite --db-name my_database.db
        ```
    
    === "PostgreSQL"
    
        Use the `--psql` flag to enable support for PostgreSQL databases.
    
        ```bash
        auto-rest --psql --db-host localhost --db-port 5432 --db-name my_database
        ```
    
    === "MySQL"
    
        Use the `--mysql` flag to enable support for MySQL databases.
    
        ```bash
        auto-rest --mysql --db-host localhost --db-port 3306 --db-name my_database
        ```
    
    === "Oracle"
    
        Use the `--oracle` flag to enable support for Oracle databases.
    
        ```bash
        auto-rest --oracle --db-host localhost --db-port 1521 --db-name my_database
        ```
    
    === "Microsoft SQL Server"
    
        Use the `--mssql` flag to enable support for Microsoft SQL Server.
        
    
        ```bash
        auto-rest --mssql --db-host localhost --db-port 1433 --db-name my_database
        ```

Auto-REST supports most common database systems out-of-the-box.
However, users can extend support to additional database systems using third party database drivers.
See the [installation instructions](install.md) for details on installing custom drivers.

!!! example "Example: Using a Custom Database Driver"

    The `--driver` option allows users to leverage specific database drivers.
    In the following example, the `postgresql+asyncpg` driver is used to connect to a PostgreSQL database.

    ```bash
    auto-rest --driver postgresql+asyncpg --db-host localhost --db-port 5432 --db-name my_database
    ```

## Enabling Optional Features

Certain API features are disabled by default.
The following table lists optional endpoints and the corresponding CLI flag.

| Endpoint            | CLI Flag           | Description                                                                                          |
|---------------------|--------------------|------------------------------------------------------------------------------------------------------|
| `/docs/`            | `--enable-docs`    | Displays HTML documentation for all available endpoints.                                             |
| `/db/<table-name>/` | `--enable-write`   | Enables support for write operations against database tables (`POST`, `PUT`, `PATCH`, and `DELETE`). |

## Customizing the Server

