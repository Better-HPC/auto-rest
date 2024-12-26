"""Factory functions for building a FastAPI application."""

import logging
from typing import Literal

import uvicorn
from fastapi import FastAPI
from sqlalchemy import Engine
from uvicorn.logging import DefaultFormatter

from .handlers import *
from .metadata import NAME, VERSION
from .models import ModelBase

__all__ = ["configure_logging", "create_app", "run_app"]

logger = logging.getLogger(__name__)


def configure_logging(level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]) -> None:
    """Configure the application logging level.

    Does not configure logging for dependencies (e.g., for uvicorn).

    Args:
        level: The python logging level.
    """

    level = level.upper()
    if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise ValueError(f"Invalid logging level: {level}")

    handler = logging.StreamHandler()
    handler.setFormatter(DefaultFormatter(fmt="%(levelprefix)s %(message)s"))
    logging.basicConfig(
        force=True,
        level=level,
        format="%(levelprefix)s %(message)s",
        handlers=[handler]
    )


def create_app(engine: Engine, models: dict[str, ModelBase], enable_meta: bool = False, enable_docs: bool = False) -> FastAPI:
    """Initialize a new FastAPI Application.

    Args:
        engine: The database engine to use in the app.
        models: Mapping of database model names to ORM classes.
        enable_meta: Add a `meta` API endpoint with DB metadata.
        enable_docs: Add a `docs` API endpoint with API documentation.

    Returns:
        A new FastAPI application.
    """

    app = FastAPI(
        title=NAME.title(),
        version=VERSION,
        summary=f"A REST API generated dynamically from the '{engine.url.database}' database schema.",
        docs_url="/docs/" if enable_docs else None,
        redoc_url=None
    )

    app.add_api_route("/", welcome_handler, methods=["GET"], include_in_schema=False)
    app.add_api_route("/version/", version_handler, methods=["GET"], tags=["Application Info"])

    if enable_meta:
        app.add_api_route(f"/meta/", create_meta_handler(engine), methods=["GET"], tags=["Application Info"])

    for model_name, model_class in models.items():
        logger.debug(f"Adding API routes for table '{model_name}'.")
        app.add_api_route(f"/db/{model_name}/", create_list_handler(engine, model_class), methods=["GET"], tags=["Database Operations"])

    return app


def run_app(app: FastAPI, server_host: str, server_port: int, log_level: str) -> None:  # pragma: no cover
    """Launch an application server.

    Args:
        app: The FastAPI application to serve.
        server_host: The server hostname.
        server_port: The server port.
        log_level: The desired server logging level.
    """

    logger.info("Launching API server...")
    uvicorn.run(app, host=server_host, port=server_port, log_level=log_level.lower())
