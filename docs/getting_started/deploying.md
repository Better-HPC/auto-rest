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
    
        ```shell
        auto-rest --sqlite --db-name my_database.db
        ```
    
    === "PostgreSQL"
    
        Use the `--psql` flag to enable support for PostgreSQL databases.
    
        ```shell
        auto-rest --psql --db-host localhost --db-port 5432 --db-name my_database
        ```
    
    === "MySQL"
    
        Use the `--mysql` flag to enable support for MySQL databases.
    
        ```shell
        auto-rest --mysql --db-host localhost --db-port 3306 --db-name my_database
        ```
    
    === "Oracle"
    
        Use the `--oracle` flag to enable support for Oracle databases.
    
        ```shell
        auto-rest --oracle --db-host localhost --db-port 1521 --db-name my_database
        ```
    
    === "Microsoft SQL Server"
    
        Use the `--mssql` flag to enable support for Microsoft SQL Server.
        
    
        ```shell
        auto-rest --mssql --db-host localhost --db-port 1433 --db-name my_database
        ```

## Using Custom Drivers

Users can extend Auto-Rest to support additional database systems using third party database drivers.
To use an alternate driver, specify the registered driver name at runtime.

!!! example "Example: Using a Custom Database Driver"

    The `--driver` option allows users to leverage specific database drivers.
    In the following example, the `postgresql+asyncpg` driver is used to connect to a PostgreSQL database.

    ```shell
    auto-rest --driver postgresql+asyncpg ...
    ```

Some database drivers support extra configuration options not available through the `auto-rest` CLI.
These options are typically driver specific and are defined using a YAML config file.
All values in the file are passed directly as arguments to the underlying `sqlalchemy.create_engine` call 
(or `create_async_engine` for asynchronous drivers).

!!! example "Example: Specifying a Database Config"

    Extra configuration arguments are defined in YAML format and passed 
    to the database engine via the `--db-config` option.

    === "CLI Call"

        ```shell
        auto-rest --driver postgresql+asyncpg --db-config config.yml  ...
        ```
    
    === "config.yml"
    
        ```yaml
        pool_size: 20
        max_overflow: 0
        echo: true
        ```


## Enabling Optional Features

Certain API features are disabled by default.
The following table lists CLI flags for enabling optional functionality.

| CLI Flag         | Description                                                                                          |
|------------------|------------------------------------------------------------------------------------------------------|
| `--enable-docs`  | Enables a `/docs/` endpoint with HTML documentation for all available endpoints.                     |
| `--enable-write` | Enables support for write operations against database tables (`POST`, `PUT`, `PATCH`, and `DELETE`). |

## Customizing Application Info

The application title and version number are both configurable at runtime.
These values are reflected across multiple endpoints, including the API documentation and version endpoint.
By default, the application title is set to "Auto-REST," and the version is set to the current Auto-REST version.

!!! example "Example: Customizing Application Info"

    Use the `--app-title` and `--app-version` arguments to customize the application name and version.

    ```shell
    auto-rest ... --app-title "My Application Name" --app-version 1.2.3
    ```

## Deploying with Docker

Better HPC provides an official docker image for the Auto-REST utility.

```shell
docker pull ghcr.io/better-hpc/auto-rest
```

Running servers with docker requires paying special attention to the network settings.
When deploying Auto-REST against a database on localhost, the database host should be set to `host.docker.internal`.
In all cases, the port of the server within the container needs to be exposed to outside traffic (`-p <HOST PORT>:<CONTAINER PORT>`).

```
docker run -p 8081:8081 auto-rest \
    --psql \
    --db-host host.docker.internal \
    --db-port <DB_PORT> \
    --db-name <DB_NAME> \
    --db-user <DB_USER> \
    --server-host 0.0.0.0 \
    --server-port 8081
```
