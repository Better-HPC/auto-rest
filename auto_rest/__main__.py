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
        args = create_argument_parser().parse_args()
        app_kwargs = format_parsed_args(args)
        run_application(**app_kwargs)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        logger.critical(str(e))


def run_application(
    db_url: str,
    pool_min: int,
    pool_max: int,
    pool_timeout: int,
    server_host: str,
    server_port: int,
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    enable_meta: bool
) -> None:
    """Launch an API server using parsed commandline options.

    Args:
        db_url: Database URL.
        pool_min: Minimum db connection pool size.
        pool_max: Maximum db connection pool size.
        pool_timeout: Seconds to wait for a connection from the pool before timeing out.
        server_host: The uvicorn server hostname.
        server_port: The uvicorn server port.
        log_level: The desired logging level
        enable_meta: Enable the `meta` API endpoint
    """

    # Initial application setup
    configure_logging(log_level)

    # Build the app
    conn_pool = create_connection_pool(db_url, pool_min, pool_max, pool_timeout)
    db_models = create_db_models(conn_pool)
    app = create_app(conn_pool, db_models, enable_meta=enable_meta)

    # Launch a uvicorn server
    run_app(app, server_host, server_port, log_level=log_level)
