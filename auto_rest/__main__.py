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
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    enable_docs: bool,
    enable_meta: bool,
    enable_write: bool,
    db_driver: str,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_pass: str,
    pool_min: int | None,
    pool_max: int | None,
    pool_out: int | None,
    server_host: str,
    server_port: int,
    oai_title: str,
    oai_version: str,
) -> None:
    """Run an Auto-REST API server.

    This function is equivalent to launching an API server from the command line
    and accepts the same arguments as those provided in the CLI.

    Args:
        log_level: Desired logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        enable_docs: Whether to enable the 'docs' API endpoint.
        enable_meta: Whether to enable the 'meta' API endpoint.
        enable_write: Whether to enable support for write operations.
        db_driver: SQLAlchemy-compatible database driver.
        db_host: Database host address.
        db_port: Database port number.
        db_name: Database name.
        db_user: Database authentication username.
        db_pass: Database authentication password.
        pool_min: Minimum number of database connections in the connection pool.
        pool_max: Maximum number of database connections in the connection pool.
        pool_out: Timeout (in seconds) for waiting on a database connection.
        server_host: API server host address.
        server_port: API server port number.
        oai_title: title for the generated OpenAPI schema.
        oai_version: version number for the generated OpenAPI schema.
    """

    configure_logging(log_level)

    # Filter out optional args.
    pool_args = dict()
    if "sqlite" not in db_driver:
        pool_args = dict(pool_size=pool_min, max_overflow=pool_max, pool_timeout=pool_out)
        pool_args = {k: v for k, v in pool_args.items() if v is not None}

    # Connect to and map the database.
    db_url = create_db_url(driver=db_driver, host=db_host, port=db_port, database=db_name, username=db_user, password=db_pass)
    db_conn = create_db_engine(db_url, **pool_args)
    db_meta = create_db_metadata(db_conn)
    db_models = create_db_models(db_meta)

    # Build and run the application.
    app = create_app(db_conn, db_models, enable_meta=enable_meta, enable_docs=enable_docs, enable_write=enable_write)
    app.openapi_schema = create_openapi_schema(app, title=oai_title, version=oai_version)

    run_app(app, server_host, server_port, log_level=log_level)
