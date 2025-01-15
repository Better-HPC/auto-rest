"""
API routers are responsible for redirecting incoming HTTP requests to the
appropriate handling logic. Router objects are created using a factory
pattern, with each router being responsible for a single application
resource. Each factory returns an `APIRouter` instance preconfigured
with request handling logic for the relevant resource. This allows
routers to be added directly to an API application instance.

!!! example "Example: Creating and Adding a Router"

   Care should be taken to avoid path conflicts when adding routers
   to an API application instance. Using a unique `prefix` value
   ensures that each router's endpoints are properly namespaced and
   unique.

    ```python
    from fastapi import FastAPI
    from auto_rest.routers import create_welcome_router

    app = FastAPI()
    welcome_router = create_welcome_router()
    app.include_router(welcome_router, prefix="/welcome")
    ```
"""

from fastapi import APIRouter
from sqlalchemy import MetaData
from starlette import status

from auto_rest.handlers import *
from auto_rest.models import DBEngine, DBModel

__all__ = [
    "create_meta_router",
    "create_model_router",
    "create_welcome_router",
]


def create_welcome_router() -> APIRouter:
    """Create an API router for returning a welcome message.

    Returns:
        An `APIRouter` with a single route for retrieving a welcome message.
    """

    router = APIRouter()
    router.add_api_route("/", create_welcome_handler(), methods=["GET"], include_in_schema=False)
    return router


def create_meta_router(engine: DBEngine, metadata: MetaData, version: str) -> APIRouter:
    """Create an API router for returning database metadata.

    Includes routes for retrieving the database driver, database schema,
    and application/schema version.

    Args:
        engine: The database engine used to facilitate database interactions.
        metadata: The metadata object containing the database schema.
        version: The version string to return.

    Returns:
        An `APIRouter` with a routes for retrieving application metadata.
    """

    router = APIRouter()
    tags = ["Application Metadata"]

    router.add_api_route("/version", create_version_handler(version), methods=["GET"], tags=tags)
    router.add_api_route("/engine", create_engine_handler(engine), methods=["GET"], tags=tags)
    router.add_api_route("/schema", create_schema_handler(metadata), methods=["GET"], tags=tags)
    return router


def create_model_router(engine: DBEngine, model: DBModel, writeable: bool = False) -> APIRouter:
    """Create an API router with endpoint handlers for the given database model.

    Args:
        engine: The SQLAlchemy engine connected to the database.
        model: The ORM model class representing a database table.
        writeable: Whether the router should include support for write operations.

    Returns:
        An APIRouter instance with routes for database operations on the model.
    """

    router = APIRouter()

    # Construct path parameters from primary key columns
    pk_columns = model.__table__.primary_key.columns
    path_params_url = "/".join(f"{{{col.name}}}" for col in pk_columns)
    path_params_openapi = {
        "parameters": [
            {
                "name": col.name,
                "in": "path",
                "required": True
            } for col in pk_columns
        ]
    }

    # Raise an error if no primary key columns are found
    # (SQLAlchemy should ensure this never happens)
    if not pk_columns:  # pragma: no cover
        raise RuntimeError(f"No primary key columns found for table {model.__tablename__}.")

    # Define routes for read operations
    router.add_api_route(
        path="/",
        methods=["GET"],
        endpoint=create_list_records_handler(engine, model),
        status_code=status.HTTP_200_OK,
        tags=[model.__name__],
        openapi_extra=path_params_openapi
    )

    router.add_api_route(
        path=f"/{path_params_url}/",
        methods=["GET"],
        endpoint=create_get_record_handler(engine, model),
        status_code=status.HTTP_200_OK,
        tags=[model.__name__],
        openapi_extra=path_params_openapi
    )

    if not writeable:
        return router

    # Define routes for write operations
    router.add_api_route(
        path="/",
        methods=["POST"],
        endpoint=create_post_record_handler(engine, model),
        status_code=status.HTTP_201_CREATED,
        tags=[model.__name__],
        openapi_extra=path_params_openapi
    )

    router.add_api_route(
        path=f"/{path_params_url}/",
        methods=["PUT"],
        endpoint=create_put_record_handler(engine, model),
        status_code=status.HTTP_200_OK,
        tags=[model.__name__],
        openapi_extra=path_params_openapi
    )

    router.add_api_route(
        path=f"/{path_params_url}/",
        methods=["PATCH"],
        endpoint=create_patch_record_handler(engine, model),
        status_code=status.HTTP_200_OK,
        tags=[model.__name__],
        openapi_extra=path_params_openapi
    )

    router.add_api_route(
        path=f"/{path_params_url}/",
        methods=["DELETE"],
        endpoint=create_delete_record_handler(engine, model),
        status_code=status.HTTP_200_OK,
        tags=[model.__name__],
        openapi_extra=path_params_openapi
    )

    return router
