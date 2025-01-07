"""
The `cli` module is responsible for defining the `auto-rest` command-line
interface. It uses the built-in argparse module to create a tailored
`ArgumentParser` instance, pre-populated with custom argument definitions.
Argument defaults, parsing, and type-casting, are handled automatically by
the parser instance.

!!! example "Example: Parsing Arguments"

    The `create_argument_parser` function returns an `ArgumentParser`
    instance which can be used as-is to parse arguments.

    ```python
    from auto_rest.cli import create_argument_parser

    parser = create_argument_parser()
    args = parser.parse_args()
    ```
"""

import importlib.metadata
from argparse import ArgumentParser, HelpFormatter

__all__ = ['VERSION', "create_argument_parser"]

VERSION = importlib.metadata.version(__package__)


def create_argument_parser(exit_on_error: bool = True) -> ArgumentParser:
    """Create a command-line argument parser with preconfigured arguments.

    Args:
        exit_on_error: Whether to exit the program on a parsing error.

    Returns:
        An argument parser instance.
    """

    formatter = lambda prog: HelpFormatter(prog, max_help_position=29)
    parser = ArgumentParser(
        prog="auto-rest",
        description="Automatically map database schemas and deploy per-table REST API endpoints.",
        exit_on_error=exit_on_error,
        formatter_class=formatter
    )

    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument(
        "--log-level",
        default="INFO",
        type=lambda x: x.upper(),
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set the logging level."
    )

    features = parser.add_argument_group(title="API features")
    features.add_argument("--enable-docs", action="store_true", help="enable the 'docs' endpoint.")
    features.add_argument("--enable-meta", action="store_true", help="enable the 'meta' endpoint.")
    features.add_argument("--enable-write", action="store_true", help="enable support for write operations.")

    driver = parser.add_argument_group("database type")
    db_type = driver.add_mutually_exclusive_group(required=True)
    db_type.add_argument("--sqlite", action="store_const", dest="db_driver", const="sqlite+aiosqlite", help="use a SQLite database driver.")
    db_type.add_argument("--psql", action="store_const", dest="db_driver", const="postgresql+asyncpg", help="use a PostgreSQL database driver.")
    db_type.add_argument("--mysql", action="store_const", dest="db_driver", const="mysql+asyncmy", help="use a MySQL database driver.")
    db_type.add_argument("--oracle", action="store_const", dest="db_driver", const="oracle+oracledb", help="use an Oracle database driver.")
    db_type.add_argument("--mssql", action="store_const", dest="db_driver", const="mssql+aiomysql", help="use a Microsoft database driver.")
    db_type.add_argument("--driver", action="store", dest="db_driver", help="use a custom database driver.")

    database = parser.add_argument_group("database location")
    database.add_argument("--db-host", help="database address to connect to.")
    database.add_argument("--db-port", type=int, help="database port to connect to.")
    database.add_argument("--db-name", required=True, help="database name or file path to connect to.")
    database.add_argument("--db-user", help="username to authenticate with.")
    database.add_argument("--db-pass", help="password to authenticate with.")

    connection = parser.add_argument_group(title="database connection")
    connection.add_argument("--pool-min", nargs="?", type=int, help="minimum number of maintained database connections.")
    connection.add_argument("--pool-max", nargs="?", type=int, help="max number of allowed database connections.")
    connection.add_argument("--pool-out", nargs="?", type=int, help="seconds to wait on connection before timing out.")

    server = parser.add_argument_group(title="server settings")
    server.add_argument("--server-host", default="127.0.0.1", help="API server host address.")
    server.add_argument("--server-port", type=int, default=8081, help="API server port number.")

    schema = parser.add_argument_group(title="api schema")
    schema.add_argument("--oai-title", default="Auto-REST", help="title for the generated OpenAPI schema.")
    schema.add_argument("--oai-version", default=VERSION, help="version number for the generated OpenAPI schema.")

    return parser
