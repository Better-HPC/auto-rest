# Auto-REST

A light-weight CLI tool for deploying dynamically generated REST APIs against relational databases.
See the [project documentation](https://better-hpc.github.io/auto-rest/) for detailed usage instructions.

## Supported Databases

Auto-REST provides built-in support for the database types listed below.
Support for additional databases can be added by installing the corresponding database drivers.
See the official documentation for instructions.

| CLI Flag   | Default Driver               | Database Type        |
|------------|------------------------------|----------------------|
| `--sqlite` | `sqlite+aiosqlite`           | SQLite               |
| `--psql`   | `postgresql+asyncpg`         | PostgreSQL           |
| `--mysql`  | `mysql+asyncmy`              | MySQL                |
| `--oracle` | `oracle+oracledb`            | Oracle               |
| `--mssql`  | `mssql+aiomysql`             | Microsoft SQL Server |
| `--driver` | Custom driver (user-defined) | Custom               |

## Quickstart

Install the CLI using your preferred Python package manager:

```shell
pipx install auto-rest-api
```

Verify that the installation completed successfully:

```shell
auto-rest --help
```

Launch an API by supplying connection parameters for your target database:

```shell
auto-rest \
  --psql 
  --db-host localhost
  --db-port 5432
  --db-name default
  --db-user jsmith
  --db-password secure123!
```

Navigate to `localhost:8081/docs/` and view the OpenAPI documentation for your dynamically generated REST API!
