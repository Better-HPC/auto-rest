"""
An **endpoint handler** is a function designed to process incoming HTTP
requests for single API endpoint. In `auto_rest`, handlers are
created dynamically using a factory pattern. This approach allows
handler logic to be customized and reused across multiple endpoints.

!!! example "Example: Creating a Handler"

    New endpoint handlers are created dynamically using factory methods.

    ```python
    welcome_handler = create_welcome_handler()
    ```

Handler functions are defined as asynchronous coroutines.
This provides improved performance when handling large numbers of
incoming requests.

!!! example "Example: Async Handlers"

    Python requires asynchronous coroutines to be run from an asynchronous
    context. In the following example, this is achieved using `asyncio.run`.

    ```python
    import asyncio

    return_value = asyncio.run(welcome_handler())
    ```

Handlers are specifically designed to integrate with the FastAPI framework,
including support for FastAPI's type hinting and data validation capabilities.
This makes it easy to incorporate handlers into a FastAPI application.

!!! example "Example: Adding a Handler to an Application"

    Use the `add_api_route` method to dynamically add handler functions to
    an existing application instance.

    ```python
    app = FastAPI(...)

    handler = create_welcome_handler()
    app.add_api_route("/", handler, methods=["GET"], ...)
    ```

!!! info "Developer Note"

    FastAPI internally performs post-processing on values returned by endpoint
    handlers before sending them in an HTTP response. For this reason, handlers
    should always be tested within the context of a FastAPI application.
"""

import logging
from typing import Awaitable, Callable

from fastapi import Depends, Response
from pydantic import create_model
from pydantic.main import ModelT
from sqlalchemy import insert, MetaData, select
from starlette.requests import Request

from .models import *
from .params import *
from .queries import *

__all__ = [
    "create_about_handler",
    "create_delete_record_handler",
    "create_engine_handler",
    "create_get_record_handler",
    "create_list_records_handler",
    "create_patch_record_handler",
    "create_post_record_handler",
    "create_put_record_handler",
    "create_schema_handler",
    "create_welcome_handler",
]

logger = logging.getLogger(__name__)


def create_welcome_handler() -> Callable[[], Awaitable[ModelT]]:
    """Create an endpoint handler that returns an application welcome message.

    Returns:
        An async function that returns a welcome message.
    """

    interface = create_model("Welcome", message=(str, "Welcome to Auto-Rest!"))

    async def welcome_handler() -> interface:
        """Return an application welcome message."""

        return interface()

    return welcome_handler


def create_about_handler(name: str, version: str) -> Callable[[], Awaitable[ModelT]]:
    """Create an endpoint handler that returns the application name and version number.

    Args:
        name: The application name.
        version: The returned version identifier.

    Returns:
        An async function that returns aplication info.
    """

    interface = create_model("Version", version=(str, version), name=(str, name))

    async def about_handler() -> interface:
        """Return the application name and version number."""

        return interface()

    return about_handler


def create_engine_handler(engine: DBEngine) -> Callable[[], Awaitable[ModelT]]:
    """Create an endpoint handler that returns configuration details for a database engine.

    Args:
        engine: Database engine to return the configuration for.

    Returns:
        An async function that returns database metadata.
    """

    interface = create_model("Meta",
        dialect=(str, engine.dialect.name),
        driver=(str, engine.dialect.driver),
        database=(str, engine.url.database),
    )

    async def meta_handler() -> interface:
        """Return metadata concerning the underlying application database."""

        return interface()

    return meta_handler


def create_schema_handler(metadata: MetaData) -> Callable[[], Awaitable[ModelT]]:
    """Create an endpoint handler that returns the database schema.

    Args:
        metadata: Metadata object containing the database schema.

    Returns:
        An async function that returns the database schema.
    """

    # Define Pydantic models for column, table, and schema level data
    column_interface = create_model("Column",
        type=(str, ...),
        nullable=(bool, ...),
        default=(str | None, None),
        primary_key=(bool, ...),
    )

    table_interface = create_model("Table", columns=(dict[str, column_interface], ...))
    schema_interface = create_model("Schema", tables=(dict[str, table_interface], ...))

    async def schema_handler() -> schema_interface:
        """Return metadata concerning the underlying application database."""

        return schema_interface(
            tables={table_name: table_interface(columns={
                column.name: column_interface(
                    type=str(column.type),
                    nullable=column.nullable,
                    default=str(column.default.arg) if column.default else None,
                    primary_key=column.primary_key
                )
                for column in table.columns
            }) for table_name, table in metadata.tables.items()}
        )

    return schema_handler


def create_list_records_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable[list[ModelT]]]:
    """Create an endpoint handler that returns a list of records from a database table.

    Args:
        engine: Database engine to use when executing queries.
        model: The ORM object to use for database manipulations.

    Returns:
        An async function that returns a list of records from the given database model.
    """

    interface = create_db_interface(model)

    async def list_records_handler(
        response: Response,
        session: DBSession = Depends(create_session_iterator(engine)),
        pagination_params: dict[str, int] = create_pagination_dependency(model),
        ordering_params: dict[str, int] = create_ordering_dependency(model),
    ) -> list[interface]:
        """Fetch a list of records from the database.

        URL query parameters are used to enable filtering, ordering, and paginating returned values.
        """

        query = select(model)
        query = apply_pagination_params(query, pagination_params, response)
        query = apply_ordering_params(query, ordering_params, response)
        result = await execute_session_query(session, query)
        return [interface.model_validate(record.__dict__) for record in result.scalars().all()]

    return list_records_handler


def create_get_record_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable[ModelT]]:
    """Create a function for handling GET requests against a single record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The ORM object to use for database manipulations.

    Returns:
        An async function that returns a single record from the given database model.
    """

    interface = create_db_interface(model)

    async def get_record_handler(
        request: Request,
        session: DBSession = Depends(create_session_iterator(engine)),
    ) -> interface:
        """Fetch a single record from the database."""

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)
        record = get_record_or_404(result)
        return interface.model_validate(record.__dict__)

    return get_record_handler


def create_post_record_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable[ModelT]]:
    """Create a function for handling POST requests against a record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The ORM object to use for database manipulations.

    Returns:
        An async function that handles record creation.
    """

    interface = create_db_interface(model)

    async def post_record_handler(
        data: interface,
        session: DBSession = Depends(create_session_iterator(engine)),
    ) -> interface:
        """Create a new record in the database."""

        query = insert(model).values(**data.dict())
        result = await execute_session_query(session, query)
        record = get_record_or_404(result)

        await commit_session(session)
        return interface.model_validate(record.__dict__)

    return post_record_handler


def create_put_record_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable[ModelT]]:
    """Create a function for handling PUT requests against a record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The ORM object to use for database manipulations.

    Returns:
        An async function that handles record updates.
    """

    interface = create_db_interface(model)

    async def put_record_handler(
        request: Request,
        data: interface,
        session: DBSession = Depends(create_session_iterator(engine)),
    ) -> interface:
        """Replace record values in the database with the provided data."""

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)
        record = get_record_or_404(result)

        for key, value in data.dict().items():
            setattr(record, key, value)

        await commit_session(session)
        return interface.model_validate(record.__dict__)

    return put_record_handler


def create_patch_record_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable[ModelT]]:
    """Create a function for handling PATCH requests against a record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The ORM object to use for database manipulations.

    Returns:
        An async function that handles record updates.
    """

    interface = create_db_interface(model)

    async def patch_record_handler(
        request: Request,
        data: interface,
        session: DBSession = Depends(create_session_iterator(engine)),
    ) -> interface:
        """Update record values in the database with the provided data."""

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)
        record = get_record_or_404(result)

        for key, value in data.dict(exclude_unset=True).items():
            setattr(record, key, value)

        await commit_session(session)
        return interface(record.__dict__)

    return patch_record_handler


def create_delete_record_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable[None]]:
    """Create a function for handling DELETE requests against a record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The ORM object to use for database manipulations.

    Returns:
        An async function that handles record deletion.
    """

    async def delete_record_handler(
        request: Request,
        session: DBSession = Depends(create_session_iterator(engine)),
    ) -> None:
        """Delete a record from the database."""

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)
        record = get_record_or_404(result)

        await delete_session_record(session, record)
        await commit_session(session)

    return delete_record_handler
