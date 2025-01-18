"""Application entrypoint triggered by calling the packaged CLI command."""

import logging
from pathlib import Path

import yaml

from .app import *
from .cli import *
from .models import *
from .routers import *

__all__ = ["main", "run_application"]

logger = logging.getLogger(__name__)


def main() -> None:  # pragma: no cover
    """Parse command-line arguments and launch an API server."""

    try:
        parser = create_cli_parser()
        args = vars(parser.parse_args())
        log_level = args.pop("log_level")

        configure_cli_logging(log_level)
        run_application(**args)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        logger.critical(str(e), exc_info=True)


def run_application(
    enable_docs: bool,
    enable_write: bool,
    db_driver: str,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_pass: str,
    db_config: Path | None,
    server_host: str,
    server_port: int,
    app_title: str,
    app_version: str,
) -> None:  # pragma: no cover
    """Run an Auto-REST API server.

    This function is equivalent to launching an API server from the command line
    and accepts the same arguments as those provided in the CLI.

    Args:
        enable_docs: Whether to enable the 'docs' API endpoint.
        enable_write: Whether to enable support for write operations.
        db_driver: SQLAlchemy-compatible database driver.
        db_host: Database host address.
        db_port: Database port number.
        db_name: Database name.
        db_user: Database authentication username.
        db_pass: Database authentication password.
        db_config: Path to a database configuration file.
        server_host: API server host address.
        server_port: API server port number.
        app_title: title for the generated OpenAPI schema.
        app_version: version number for the generated OpenAPI schema.
    """

    # Connect to and map the database.
    logger.info(f"Mapping database schema for {db_name}.")
    db_url = create_db_url(driver=db_driver, host=db_host, port=db_port, database=db_name, username=db_user, password=db_pass)
    db_kwargs = yaml.safe_load(db_config.read_text()) if db_config else {}
    db_conn = create_db_engine(db_url, **db_kwargs)
    db_meta = create_db_metadata(db_conn)
    db_models = create_db_models(db_meta)

    # Build an empty application and dynamically add the requested functionality.
    logger.info("Creating API application.")
    app = create_app(app_title, app_version, enable_docs)
    app.include_router(create_welcome_router(), prefix="")
    app.include_router(create_meta_router(db_conn, db_meta, app_title, app_version), prefix="/meta")

    for model_name, model in db_models.items():
        logger.info(f"Adding `/db/{model_name}` endpoint.")
        app.include_router(create_model_router(db_conn, model, enable_write), prefix=f"/db/{model_name}")

    # Launch the API server.
    logger.info(f"Launching API server on http://{server_host}:{server_port}.")
    run_app(app, server_host, server_port)
