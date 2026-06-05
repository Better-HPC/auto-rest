"""
The `cli` module manages input/output operations for the application's
command line interface (CLI). Application inputs are parsed using the
built-in `argparse` module while output messages are handled using the
Python `logging` library.

!!! example "Example: Parsing Arguments"

    The `create_argument_parser` function returns an `ArgumentParser`
    instance with pre-populated argument definitions.

    ```python
    from auto_rest.cli import create_argument_parser

    parser = create_argument_parser()
    args = parser.parse_args()
    print(vars(args))
    ```

!!! example "Example: Enabling Console Logging"

    The `configure_cli_logging` method overrides any existing logging
    configurations and enables console logging according to the provided log
    level.

    ```python
    from auto_rest.cli import configure_cli_logging

    configure_cli_logging(log_level="INFO")
    ```
"""

import functools
import importlib.metadata
import logging.config
from argparse import ArgumentParser, HelpFormatter
from pathlib import Path

__all__ = ["configure_cli_logging", "create_cli_parser", "VERSION"]

VERSION = importlib.metadata.version("auto-rest-api")


def configure_cli_logging(level: str) -> None:
    """Enable console logging with the specified application log level.

    Calling this method overrides and removes all previously configured
    logging configurations.

    Args:
        level: The Python logging level (e.g., "DEBUG", "INFO", etc.).
    """

    # Normalize and validate the logging level.
    level = level.upper()
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        raise ValueError(f"Invalid logging level: {level}")

    msg_prefix = "%(log_color)s%(levelname)-8s%(reset)s (%(asctime)s) [%(correlation_id)s] "
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": True,
        "filters": {
            "correlation_id": {
                "()": "asgi_correlation_id.CorrelationIdFilter",
                "uuid_length": 8,
                "default_value": "-" * 8
            },
        },
        "formatters": {
            "app": {
                "()": "colorlog.ColoredFormatter",
                "format": msg_prefix + "%(message)s",
            },
            "access": {
                "()": "colorlog.ColoredFormatter",
                "format": msg_prefix + "%(ip)s:%(port)s - %(method)s %(endpoint)s - %(message)s",
            }
        },
        "handlers": {
            "app": {
                "class": "colorlog.StreamHandler",
                "formatter": "app",
                "filters": ["correlation_id"],
            },
            "access": {
                "class": "colorlog.StreamHandler",
                "formatter": "access",
                "filters": ["correlation_id"],
            }
        },
        "loggers": {
            "auto_rest": {
                "handlers": ["app"],
                "level": level,
                "propagate": False
            },
            "auto_rest.access": {
                "handlers": ["access"],
                "level": level,
                "propagate": False
            },
            "auto_rest.query": {
                "handlers": ["app"],
                "level": level,
                "propagate": False
            }
        }
    })


def create_cli_parser(exit_on_error: bool = True) -> ArgumentParser:
    """Create a command-line argument parser with preconfigured arguments.

    Args:
        exit_on_error: Whether to exit the program on a parsing error.

    Returns:
        An argument parser instance.
    """

    formatter = functools.partial(HelpFormatter, max_help_position=29)
    parser = ArgumentParser(
        prog="auto-rest",
        description="Automatically map database schemas and deploy per-table API endpoints.",
        exit_on_error=exit_on_error,
        formatter_class=formatter
    )

    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument(
        "--log-level",
        default="INFO",
        type=lambda x: x.upper(),
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set the logging level"
    )

    driver = parser.add_argument_group("database type", description="The driver to use when connecting to the database.")
    db_type = driver.add_mutually_exclusive_group(required=True)
    db_type.add_argument("--sqlite", action="store_const", dest="db_driver", const="sqlite+aiosqlite", help="use a SQLite database driver")
    db_type.add_argument("--psql", action="store_const", dest="db_driver", const="postgresql+asyncpg", help="use a PostgreSQL database driver")
    db_type.add_argument("--mysql", action="store_const", dest="db_driver", const="mysql+aiomysql", help="use a MySQL database driver")
    db_type.add_argument("--oracle", action="store_const", dest="db_driver", const="oracle+oracledb", help="use an Oracle database driver")
    db_type.add_argument("--mssql", action="store_const", dest="db_driver", const="mssql+pymssql", help="use a Microsoft database driver")
    db_type.add_argument("--driver", action="store", dest="db_driver", help="use a custom database driver")

    database = parser.add_argument_group("database settings", description="Database connection and authentication settings.")
    database.add_argument("--db-host", help="database address to connect to")
    database.add_argument("--db-port", type=int, help="database port to connect to")
    database.add_argument("--db-name", required=True, help="database name or file path to connect to")
    database.add_argument("--db-user", help="username to authenticate with")
    database.add_argument("--db-pass", help="password to authenticate with")
    database.add_argument("--db-config", action="store", type=Path, help="path to a database configuration file")

    server = parser.add_argument_group(title="server settings", description="Options for the deployed API server.")
    server.add_argument("--server-host", default="127.0.0.1", help="API server host address")
    server.add_argument("--server-port", type=int, default=8081, help="API server port number")

    methods = parser.add_argument_group(title="Server functionality", description="Enable REST functionality in the deployed server.")
    methods.add_argument("--enable-list", action="store_true", help="enable GET for listing records")
    methods.add_argument("--enable-get", action="store_true", help="enable GET for fetching single records")
    methods.add_argument("--enable-post", action="store_true", help="enable POST for creating records")
    methods.add_argument("--enable-put", action="store_true", help="enable PUT for replacing records")
    methods.add_argument("--enable-patch", action="store_true", help="enable PATCH for updating records")
    methods.add_argument("--enable-delete", action="store_true", help="enable DELETE for deleting records")

    mcp = parser.add_argument_group(title="MCP functionality", description="Wraps enabled REST endpoints as MCP tools.")
    mcp.add_argument("--enable-mcp", action="store_true", default=False, help="enable an MCP server at /mcp")

    schema = parser.add_argument_group(title="Schema settings", description="Customize the deployed application's metadata.")
    schema.add_argument("--app-title", default="Auto-REST", help="title for the rendered API schema")
    schema.add_argument("--app-version", default=VERSION, help="version number for the rendered API schema")

    return parser
