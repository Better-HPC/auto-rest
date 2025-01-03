"""Application entrypoint triggered by calling the packaged CLI command."""

import logging
from typing import Literal

from auto_rest.app import *
from auto_rest.cli import *
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
    server_host: str,
    server_port: int,
    enable_docs: bool,
    enable_meta: bool,
    pool_min: int | None,
    pool_max: int | None,
    pool_out: int | None,
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
) -> None:
    """Run an Auto-REST API server.

    This function accepts the same arguments as the CLI and is functionally
    equivalent as launching an API server from the command line.

    Args:
        db_driver: The sqlalchemy compatible database driver to use.
        db_host: The database host address.
        db_port: The database port number.
        db_name: The database name to connect to.
        db_user: The username for authenticating with the database.
        db_pass: The password for authenticating with the database.
        server_host: The API server host address.
        server_port: The API server port number.
        enable_docs: Whether to enable the 'docs' API endpoint.
        enable_meta: Whether to enable the 'meta' API endpoint.
        pool_min: Minimum number of maintained database connections.
        pool_max: Maximum number of allowed database connections.
        pool_out: Timeout in seconds to wait for a database connection before timing out.
        log_level: The desired logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
    """

    configure_logging(log_level)

    # Filter out optional args
    pool_args = dict(pool_size=pool_min, max_overflow=pool_max, pool_timeout=pool_out)
    pool_args = {k: v for k, v in pool_args.items() if v is not None}

    # Connect to and map the database
    db_url = create_db_url(driver=db_driver, host=db_host, port=db_port, database=db_name, username=db_user, password=db_pass)
    db_conn = create_db_engine(db_url, **pool_args)
    db_meta = create_db_metadata(db_conn)
    db_models = create_db_models(db_meta)

    # Build and launch the app
    app = create_app(db_conn, db_models, enable_meta=enable_meta, enable_docs=enable_docs)
    run_app(app, server_host, server_port, log_level=log_level)
