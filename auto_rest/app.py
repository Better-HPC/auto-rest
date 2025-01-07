"""Factory functions for building FastAPI application instances."""

import logging
import re
from typing import Literal

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.openapi.utils import get_openapi
from starlette import status
from uvicorn.logging import DefaultFormatter

from .handlers import *
from .models import DBEngine, DBModel

__all__ = [
    "configure_logging",
    "create_app",
    "create_openapi_schema",
    "create_route_handlers",
    "run_app"
]

logger = logging.getLogger(__name__)


def configure_logging(level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]) -> None:
    """Configure the application logging level.

    Does not configure logging for dependencies (e.g., for uvicorn).

    Args:
        level: The Python logging level.
    """

    # Normalize and validate the logging level
    level = level.upper()
    if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise ValueError(f"Invalid logging level: {level}")

    # Set up logging with a stream handler
    handler = logging.StreamHandler()
    handler.setFormatter(DefaultFormatter(fmt="%(levelprefix)s %(message)s"))
    logging.basicConfig(
        force=True,
        level=level,
        format="%(levelprefix)s %(message)s",
        handlers=[handler]
    )


def create_route_handlers(engine: DBEngine, model: DBModel) -> APIRouter:
    """Create an API router with endpoint handlers for the given database model.

    Args:
        engine: The SQLAlchemy engine connected to the database.
        model: The ORM model class representing a database table.

    Returns:
        An APIRouter instance with routes for database operations on the model.
    """

    router = APIRouter()

    # Construct path parameters for primary key columns
    pk_columns = model.__table__.primary_key.columns
    path_params = "/".join(f"{{{col.name}}}" for col in pk_columns)

    # Raise an error if no primary key columns are found (should never happen)
    if not pk_columns:  # pragma: no cover
        raise RuntimeError(f"No primary key columns found for table {model.__tablename__}.")

    # Define routes for the CRUD operations
    router.add_api_route(
        path="/",
        methods=["GET"],
        endpoint=create_list_records_handler(engine, model),
        status_code=status.HTTP_200_OK,
        tags=[model.__name__]
    )

    router.add_api_route(
        path="/",
        methods=["POST"],
        endpoint=create_post_record_handler(engine, model),
        status_code=status.HTTP_201_CREATED,
        tags=[model.__name__]
    )

    router.add_api_route(
        path=f"/{path_params}/",
        methods=["GET"],
        endpoint=create_get_record_handler(engine, model),
        status_code=status.HTTP_200_OK,
        tags=[model.__name__]
    )

    router.add_api_route(
        path=f"/{path_params}/",
        methods=["PUT"],
        endpoint=create_put_record_handler(engine, model),
        status_code=status.HTTP_200_OK,
        tags=[model.__name__]
    )

    router.add_api_route(
        path=f"/{path_params}/",
        methods=["PATCH"],
        endpoint=create_patch_record_handler(engine, model),
        status_code=status.HTTP_200_OK,
        tags=[model.__name__]
    )

    router.add_api_route(
        path=f"/{path_params}/",
        methods=["DELETE"],
        endpoint=create_delete_record_handler(engine, model),
        status_code=status.HTTP_200_OK,
        tags=[model.__name__]
    )

    return router


def create_openapi_schema(app, title: str, version: str) -> dict[str, any]:
    """Create an OpenAPI schema generator for a FastAPI app.

    Args:
        app: The FastAPI application instance.
        title: Title for the generated schema.
        version: Version number for the generated schema.

    Returns:
        An OpenAPI schema definition for the application.
    """

    openapi_schema = get_openapi(
        title=title,
        version=version,
        routes=app.routes,
    )

    # Ensure path parameters are defined for dynamically generated paths
    path_parameter_pattern = re.compile(r"\{([^{}]+)\}")
    for path, methods in openapi_schema["paths"].items():
        path_params = path_parameter_pattern.findall(path)

        # Override existing parameter definitions
        for method in methods.values():
            method.setdefault("parameters", []).extend(
                {"name": param, "in": "path", "required": True} for param in path_params
            )

    return openapi_schema


def create_app(
    engine: DBEngine,
    models: dict[str, DBModel],
    enable_meta: bool = False,
    enable_docs: bool = False,
) -> FastAPI:
    """Initialize a new FastAPI Application.

    Args:
        engine: The database engine to use in the app.
        models: Mapping of database model names to ORM classes.
        enable_meta: Add a `meta` API endpoint with DB metadata.
        enable_docs: Add a `docs` API endpoint with API documentation.

    Returns:
        A new FastAPI application.
    """

    logging.info("Building API application.")
    if enable_docs:
        logging.debug("Enabling '/docs/' endpoint.")

    # Initialize FastAPI app
    app = FastAPI(
        docs_url="/docs/" if enable_docs else None,
        redoc_url=None
    )

    # Add top-level API routes
    app.add_api_route("/", create_welcome_handler(), methods=["GET"], include_in_schema=False)
    app.add_api_route("/version/", create_version_handler(), methods=["GET"], tags=["Application Metadata"])

    # Optionally add a route for database metadata
    if enable_meta:
        logging.debug("Enabling '/meta/' endpoint.")
        app.add_api_route(f"/meta/", create_meta_handler(engine), methods=["GET"], tags=["Application Metadata"])

    # Add routes for each database model.
    for model_name, model_class in models.items():
        logging.debug(f"Adding endpoints for '{model_name}'.")
        router = create_route_handlers(engine, model_class)
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
