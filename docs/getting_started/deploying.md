# Deploying an API

The following instructions outline how to deploy an API server using the `auto-rest` command.
For a full list of application arguments, see the application help text (`auto-rest --help`).

## Launching an API

Deploying an API server requires specifying the database type and connection settings.
Using the provided values, Auto-REST will automatically connect to the database, map the database schema, and deploy an
API server with dynamically generated endpoints.

!!! example

    === "SQLite"
    
        The `--sqlite` flag enables support for SQLite.
        Unlike traditional database systems, SQLite is file based and requires fewer conenction settings.
        The file path to the database should be specified using the `--db-host` option.
    
        ```bash
        auto-rest --sqlite --db-host my_database.db
        ```
    
    === "PostgreSQL"
    
        Use the `--psql` flag to enable support for PostgreSQL databases.
        The `--db-name` argument is optional when connecting to the default database.
    
        ```bash
        auto-rest --psql --db-host localhost --db-port 5432 --db-name my_database
        ```
    
    === "MySQL"
    
        Use the `--mysql` flag to enable support for MySQL databases.
        The `--db-name` argument is optional when connecting to the default database.
    
        ```bash
        auto-rest --mysql --db-host localhost --db-port 3306 --db-name my_database
        ```
    
    === "Oracle"
    
        Use the `--oracle` flag to enable support for Oracle databases.
        The `--db-name` argument is optional when connecting to the default database.
    
        ```bash
        auto-rest --oracle --db-host localhost --db-port 1521 --db-name my_database
        ```
    
    === "Microsoft SQL Server"
    
        Use the `--mssql` flag to enable support for Microsoft SQL Server.
        The `--db-name` argument is optional when connecting to the default database.
        
    
        ```bash
        auto-rest --mssql --db-host localhost --db-port 1433 --db-name my_database
        ```

The generated API server is launched on port 8081 by default, but can be customized to any valid port value.

!!! example

    ```bash
    auto-rest ... --server-port 8888
    ```

## Enabling Extra Endpoints

Certain API endpoints are disabled by default and are only included in the generated API upon request.
The following table lists optional endpoints and the corresponding CLI flag.

| Endpoint | CLI Flag        | Description                                                         |
|----------|-----------------|---------------------------------------------------------------------|
| `/docs/` | `--enable-docs` | Displays HTML documentation for all available endpoints.            |
| `/meta/` | `--enable-meta` | Returns meta data concerning the database used to generate the API. |

## Using Custom Drivers

Auto-REST supports custom database drivers in addition to the built-in ones (SQLite, PostgreSQL, MySQL, Oracle, and
Microsoft SQL Server).
To use a custom database driver, specify the driver with the `--driver` flag.
The driver argument must be a qualified driver name and be supported by SQAlchemy.
See the [installation instructions](install.md) for details on installing alternative drivers.

!!! example

    The following example uses the `postgresql+asyncpg` database driver for PostgreSQL.

    ```bash
    auto-rest --driver postgresql+asyncpg --db-host localhost --db-port 1234 --db-name my_database
    ```

## Scaling the Connection Pool

Auto-REST maintains a pool of active database connections at all times.
This minimizes application latency and improves overall performance.
However, the default pool size may not be suitable for all use cases and can be customized.

!!! example

    The following example maintains a minimum of 10 active database connections while allowing up to 50 connections total.
    Connection requests will time out after 30 seconds.

    ```bash
    auto-rest --psql --db-host localhost --db-port 5432 --db-name my_database --pool-min 10 --pool-max 50 --pool-out 30
    ```
