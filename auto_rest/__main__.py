"""Application entrypoint triggered by calling the packaged CLI command."""

import logging
from typing import Literal

from .app import *
from .cli import *
from .models import *

__all__ = ["main", "run_application"]

logger = logging.getLogger(__name__)


def main() -> None:
    """Parse command-line arguments and launch an API server."""

    try:
        parser = create_argument_parser()
        args = parser.parse_args()
        run_application(**vars(args))

    except KeyboardInterrupt:
        pass

    except Exception as e:
        logger.critical(str(e))


def run_application(
    db_driver: str,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_pass: str,
    pool_min: int,
    pool_max: int,
    pool_out: int,
    server_host: str,
    server_port: int,
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    enable_docs: bool,
    enable_meta: bool,
) -> None:
    """Map a database schema and launch an API server.

    This function is functionally equivalent to launching an API server from the
    CLI, except it is callable as a Python function.

    Args:
        db_driver: The sqlalchemy compatible database driver to use.
        db_host: The database host address.
        db_port: The database port number.
        db_name: The database name to connect to.
        db_user: The username for authenticating with the database.
        db_pass: The password for authenticating with the database.
        pool_min: Minimum number of maintained database connections.
        pool_max: Maximum number of allowed database connections.
        pool_out: Timeout in seconds to wait for a database connection before timing out.
        server_host: The API server host address.
        server_port: The API server port number.
        log_level: The desired logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        enable_docs: Whether to enable the 'docs' API endpoint.
        enable_meta: Whether to enable the 'meta' API endpoint.
    """

    # Initial application setup
    configure_logging(log_level)

    # Connect to the database
    db_url = create_db_url(driver=db_driver, host=db_host, port=db_port, database=db_name, username=db_user, password=db_pass)
    db_conn = create_db_engine(db_url, pool_size=pool_min, max_overflow=pool_max, pool_timeout=pool_out)

    # Build the app
    db_models = create_db_models(db_conn)
    app = create_app(db_conn, db_models, enable_meta=enable_meta, enable_docs=enable_docs)

    # Launch a uvicorn server
    run_app(app, server_host, server_port, log_level=log_level)
