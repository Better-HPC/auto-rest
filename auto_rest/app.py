"""Factory functions for building FastAPI application instances."""

import logging
from typing import Literal

import uvicorn
from fastapi import APIRouter, FastAPI
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from uvicorn.logging import DefaultFormatter

from .handlers import *
from .dist import version
from .handlers import create_post_record_handler
from .models import ModelBase

__all__ = [
    "configure_logging",
    "create_app",
    "create_router",
    "run_app",
]

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


def create_router(engine: Engine | AsyncEngine, model: ModelBase) -> APIRouter:
    """Create an API router with endpoint handlers for the given database model.

    Args:
        engine: The SQLAlchemy engine connected to the database.
        model: The ORM model class representing a database table.

    Returns:
        An APIRouter instance with routes for database operations on the model.
    """

    router = APIRouter()

    # Add table level endpoint for listing records
    list_handler = create_list_records_handler(engine, model)
    router.add_api_route("/", list_handler, methods=["GET"], tags=[f"{model.__name__}"])

    post_handler = create_post_record_handler(engine, model)
    router.add_api_route("/", post_handler, methods=["POST"], tags=[f"{model.__name__}"])

    # Determine the path for per-record endpoints
    pk_columns = model.__table__.primary_key.columns
    path_params = '/'.join(f'{{{col.name}}}' for col in pk_columns)

    # Per-record endpoints are only added for tables with primary keys
    if not pk_columns:
        return router

    # Add GET operation against single record
    get_record_handler = create_get_record_handler(engine, model)
    router.add_api_route(f"/{path_params}/", get_record_handler, methods=["GET"], tags=[f"{model.__name__}"])

    return router


def create_app(engine: Engine | AsyncEngine, models: dict[str, ModelBase], enable_meta: bool = False, enable_docs: bool = False) -> FastAPI:
    """Initialize a new FastAPI Application.

    Args:
        engine: The database engine to use in the app.
        models: Mapping of database model names to ORM classes.
        enable_meta: Add a `meta` API endpoint with DB metadata.
        enable_docs: Add a `docs` API endpoint with API documentation.

    Returns:
        A new FastAPI application.
    """

    logging.info('Building API application.')

    app = FastAPI(
        title="Auto-REST",
        version=version,
        summary=f"A REST API generated dynamically from the '{engine.url.database}' database schema.",
        docs_url="/docs/" if enable_docs else None,
        redoc_url=None
    )

    # Add top level API routes
    app.add_api_route("/", welcome_handler, methods=["GET"], include_in_schema=False)
    app.add_api_route("/version/", version_handler, methods=["GET"], tags=["Application Metadata"])
    if enable_meta:
        app.add_api_route(f"/meta/", create_meta_handler(engine), methods=["GET"], tags=["Application Metadata"])

    # Add routes for each table
    for model_name, model_class in models.items():
        route = f"/db/{model_name}"
        router = create_router(engine, model_class)

        logging.debug(f"Adding API route for '{route}'.")
        app.include_router(router, prefix=route)

    return app


def run_app(app: FastAPI, server_host: str, server_port: int, log_level: str) -> None:  # pragma: no cover
    """Launch an application server.

    Args:
        app: The FastAPI application to serve.
        server_host: The server hostname.
        server_port: The server port.
        log_level: The desired server logging level.
    """

    logger.info("Launching API server.")
    uvicorn.run(app, host=server_host, port=server_port, log_level=log_level.lower())
