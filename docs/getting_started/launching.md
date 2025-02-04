# Launching Auto-Rest

The following instructions provide a general introduction to the `auto-rest` command.
For a full list of available options, see the application help text (`auto-rest --help`).

## Launching an API

Deploying an API server requires specifying the database type and connection settings.
Using the provided arguments, `auto-rest` will automatically connect to the database,
map the database schema, and deploy a customized API server.

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
    In the following example, the `postgresql+asyncpg` driver is used for a PostgreSQL database.

    ```shell
    auto-rest --driver postgresql+asyncpg ...
    ```

Some database drivers support extra configuration options not available through the `auto-rest` CLI.
These options are typically driver specific and are provided using a YAML config file.
All values in the file are passed directly as arguments to the underlying `sqlalchemy.create_engine` call
(or `create_async_engine` for asynchronous drivers).

!!! example "Example: Specifying a Database Config"

    Extra configuration arguments can be passed to the database engine using the `--db-config` option
    and a YAML config file.

    ```shell
    auto-rest --driver postgresql+asyncpg --db-config config.yml  ...
    ```

## Customizing Application Info

The application title and version number are both configurable at runtime.
These values are reflected across multiple endpoints, including the dynamically generated OpenAPI documentation.
By default, the application title is set to `Auto-REST` and the version is set to the current Auto-REST version.

!!! example "Example: Customizing Application Info"

    Use the `--app-title` and `--app-version` arguments to customize the application name and version.

    ```shell
    auto-rest --app-title "My Application Name" --app-version 1.2.3 ...
    ```

## Deploying with Docker

The official Auto-REST docker image is available for download from the GitHub Container Registry.

!!! example "Example: Pulling The Docker Image"

    The default Docker image includes the latest release of the Auto-REST software.
    [Alternative versions](ghcr.io/better-hpc/auto-rest) are available via Docker tags.

    ```shell
    docker pull ghcr.io/better-hpc/auto-rest
    ```

Running Auto-REST within Docker requires paying special attention to the Docker network settings.
When deploying Auto-REST against a database on `localhost`, the database host should be set to `host.docker.internal`.
This will ensure the service within the container can locate the database running on the parent machine.
In all cases, the port of the server within the container needs to be exposed to outside traffic (
`-p <HOST PORT>:<CONTAINER PORT>`).

!!! example "Example: Launching a Docker Container"

    When running Auto-REST from within a Docker container, the Docker network settings must be configured to
    allow traffic between the client/server and the server/database. Use `host.docker.internal` when refering
    to the parent machine.

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
