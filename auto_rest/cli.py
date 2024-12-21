"""Utilities for parsing and formatting command line arguments."""

from argparse import ArgumentParser, Namespace

from sqlalchemy import URL

from .metadata import SUMMARY, VERSION

__all__ = ["create_argument_parser", "format_parsed_args"]


def create_argument_parser(exit_on_error: bool = True) -> ArgumentParser:
    """Create a command-line argument parser with predefined options / arguments.

    Args:
        exit_on_error: Whether to exit the program on a parsing error (useful in testing).

    Returns:
        An argument parser instance.
    """

    parser = ArgumentParser(
        prog="auto-rest",
        description=SUMMARY,
        exit_on_error=exit_on_error
    )

    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument(
        "--log-level",
        default="INFO",
        type=lambda x: x.upper(),
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set the logging level."
    )

    database = parser.add_argument_group("database settings")

    db_type = database.add_mutually_exclusive_group(required=True)
    db_type.add_argument("--sqlite", action="store_true", help="use a SQLite database.")
    db_type.add_argument("--psql", action="store_true", help="use a PostgreSQL database.")
    db_type.add_argument("--mysql", action="store_true", help="use a MySQL database.")

    database.add_argument("--db-host", required=True, help="database address to connect to.")
    database.add_argument("--db-port", type=int, help="database port to connect to.")
    database.add_argument("--db-name", help="database name to connect to.")
    database.add_argument("--db-user", help="username to authenticate with.")
    database.add_argument("--db-pass", help="password to authenticate with.")

    features = parser.add_argument_group(title="API features")
    features.add_argument("--enable-meta", action="store_true", help="enable the 'meta' endpoint.")

    connection = parser.add_argument_group(title="connection pool settings")
    connection.add_argument("--pool-min", type=int, default=50, help="minimum number of maintained database connections.")
    connection.add_argument("--pool-max", type=int, default=100, help="max number of allowed database connections.")
    connection.add_argument("--pool-out", type=int, default=30, help="seconds to wait on connection before timing out.")

    server = parser.add_argument_group(title="server settings")
    server.add_argument("--server-host", default="127.0.0.1", help="API server host address.")
    server.add_argument("--server-port", type=int, default=8081, help="API server port number.")

    return parser


def format_parsed_args(args: Namespace) -> dict[str, any]:
    """Convert parsed commandline arguments into a convenient format.
    
    Args:
        args: Argument namespace returned from the application command line parser.

    Returns:
        A dictionary of application arguments.
    """

    driver_flags: [str, bool] = {
        "sqlite": args.sqlite,
        "postgresql+asyncpg": args.psql,
        "mysql": args.mysql
    }

    driver = next(p for p, a in driver_flags.items() if a)
    db_url = URL.create(
        drivername=driver,
        username=args.db_user,
        password=args.db_pass,
        host=args.db_host,
        port=args.db_port,
        database=args.db_name
    )

    return {
        "db_url": str(db_url),
        "pool_min": args.pool_min,
        "pool_max": args.pool_max,
        "pool_timeout": args.pool_out,
        "server_host": args.server_host,
        "server_port": args.server_port,
        "log_level": args.log_level,
        "enable_meta": args.enable_meta
    }
