"""Factory functions for building FastAPI application instances."""

import logging
from typing import Literal

import uvicorn
from fastapi import APIRouter, FastAPI
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette import status
from uvicorn.logging import DefaultFormatter

from .dist import version
from .handlers import *
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


def create_router(engine: Engine | AsyncEngine, model: ModelBase, writable: bool = False) -> APIRouter:
    """Create an API router with endpoint handlers for the given database model.

    Args:
        engine: The SQLAlchemy engine connected to the database.
        model: The ORM model class representing a database table.
        writable: Whether to add support for write operations (POST, PUT, PATCH, DELETE).

    Returns:
        An APIRouter instance with routes for database operations on the model.
    """

    router = APIRouter()

    # Add GET support against the table
    router.add_api_route(
        path="/",
        methods=["GET"],
        endpoint=create_list_records_handler(engine, model),
        status_code=status.HTTP_200_OK,
        tags=[model.__name__]
    )

    # Add POST support against the table
    if writable:
        router.add_api_route(
            path="/",
            methods=["POST"],
            endpoint=create_post_record_handler(engine, model),
            status_code=status.HTTP_201_CREATED,
            tags=[model.__name__]
        )

    # Per-record endpoints are only added for tables with primary keys
    if pk_columns := model.__table__.primary_key.columns:
        path_params = '/'.join(f'{{{col.name}}}' for col in pk_columns)

        # Add GET support against a single record
        router.add_api_route(
            path=f"/{path_params}/",
            methods=["GET"],
            endpoint=create_get_record_handler(engine, model),
            status_code=status.HTTP_200_OK,
            tags=[model.__name__]
        )

    if pk_columns and writable:

        # Add PUT support against a single record
        router.add_api_route(
            path=f"/{path_params}/",
            methods=["PUT"],
            endpoint=create_put_record_handler(engine, model),
            status_code=status.HTTP_200_OK,
            tags=[model.__name__]
        )

        # Add PATCH support against a single record
        router.add_api_route(
            path=f"/{path_params}/",
            methods=["PATCH"],
            endpoint=create_patch_record_handler(engine, model),
            status_code=status.HTTP_200_OK,
            tags=[model.__name__]
        )

        # Add DELETE support against a single record
        router.add_api_route(
            path=f"/{path_params}/",
            methods=["DELETE"],
            endpoint=create_delete_record_handler(engine, model),
            status_code=status.HTTP_200_OK,
            tags=[model.__name__]
        )

    return router


def create_app(
    engine: Engine | AsyncEngine,
    models: dict[str, ModelBase],
    enable_meta: bool = False,
    enable_docs: bool = False,
    enable_write: bool = False,
) -> FastAPI:
    """Initialize a new FastAPI Application.

    Args:
        engine: The database engine to use in the app.
        models: Mapping of database model names to ORM classes.
        enable_meta: Add a `meta` API endpoint with DB metadata.
        enable_docs: Add a `docs` API endpoint with API documentation.
        enable_write: Add support for write operations.

    Returns:
        A new FastAPI application.
    """

    logging.info('Building API application.')

    if enable_docs:
        logging.info("Enabling '/docs/' endpoint.")

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
        logging.info("Enabling '/meta/' endpoint.")
        app.add_api_route(f"/meta/", create_meta_handler(engine), methods=["GET"], tags=["Application Metadata"])

    # Add routes for each table
    for model_name, model_class in models.items():
        logging.debug(f"Adding endpoints for '{model_name}'.")
        router = create_router(engine, model_class, writable=enable_write)
        app.include_router(router, prefix=f"/db/{model_name}")

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
