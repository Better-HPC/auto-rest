"""Application entrypoint triggered by calling the packaged CLI command."""

import logging

import uvicorn
from fastapi import FastAPI

from .cli import *
from .models import *
from .routers import *

__all__ = ["main", "run_application"]

logger = logging.getLogger(__name__)


def main() -> None:
    """Parse command-line arguments and launch an API server."""

    try:
        parser = create_cli_parser()
        args = vars(parser.parse_args())

        configure_cli_logging(args.pop('log_level'))
        run_application(**args)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        logger.critical(str(e), exc_info=True)


def run_application(
    enable_docs: bool,
    enable_meta: bool,
    enable_version: bool,
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
    app_title: str,
    app_version: str,
) -> None:
    """Run an Auto-REST API server.

    This function is equivalent to launching an API server from the command line
    and accepts the same arguments as those provided in the CLI.

    Args:
        enable_docs: Whether to enable the 'docs' API endpoint.
        enable_meta: Whether to enable the 'meta' API endpoint.
        enable_version: Whether to enable the 'version' API endpoint.
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
        app_title: title for the generated OpenAPI schema.
        app_version: version number for the generated OpenAPI schema.
    """

    # Connect to and map the database.
    logger.info(f"Mapping database schema for {db_name}.")
    db_url = create_db_url(driver=db_driver, host=db_host, port=db_port, database=db_name, username=db_user, password=db_pass)
    db_conn = create_db_engine(db_url, pool_min=pool_min, pool_max=pool_max, pool_out=pool_out)
    db_meta = create_db_metadata(db_conn)
    db_models = create_db_models(db_meta)

    # Build an empty application and dynamically add the requested functionality.
    app = FastAPI(title=app_title, version=app_version, docs_url="/docs/" if enable_docs else None, redoc_url=None)
    app.include_router(create_welcome_router(), prefix="")

    if enable_version:
        logger.info("Adding `/version/` endpoint.")
        app.include_router(create_version_router(app_version), prefix="/version")

    if enable_meta:
        logger.info("Adding `/meta/` endpoint.")
        app.include_router(create_meta_router(db_conn), prefix="/meta")

    for model_name, model in db_models.items():
        logger.info(f"Adding `/db/{model_name}` endpoint.")
        app.include_router(create_model_router(db_conn, model, enable_write), prefix=f"/db/{model_name}")

    # Launch the API server.
    logger.info(f"Launching API server on http://{server_host}:{server_port}.")
    uvicorn.run(app, host=server_host, port=server_port, log_level="error")
