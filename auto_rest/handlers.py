"""Functions for handling incoming HTTP requests and generating responses."""

import importlib.metadata
import logging
from typing import Awaitable, Callable, cast

from fastapi import Depends, Response
from pydantic import create_model
from sqlalchemy import insert, select
from starlette.requests import Request

from .models import *
from .params import *
from .queries import *

__all__ = [
    "create_delete_record_handler",
    "create_get_record_handler",
    "create_list_records_handler",
    "create_meta_handler",
    "create_patch_record_handler",
    "create_post_record_handler",
    "create_put_record_handler",
    "create_version_handler",
    "create_welcome_handler",
]

logger = logging.getLogger(__name__)


def create_welcome_handler() -> Callable[[], Awaitable]:
    """Create a function that returns an application welcome message in JSON format."""

    welcome_message = "Welcome to Auto-Rest!"
    interface = create_model("Welcome", message=(str, welcome_message))

    async def welcome_handler() -> interface:
        """Return a welcome message in JSON format."""

        return cast({"message": welcome_message}, interface)

    return welcome_handler


def create_version_handler() -> Callable[[], Awaitable]:
    """Create a function that returns a dictionary with the application version number."""

    version = importlib.metadata.version(__package__)
    interface = create_model("Version", version=(str, version))

    async def version_handler() -> interface:
        """Return the application version number in JSON format."""

        return cast({"version": version}, interface)

    return version_handler


def create_meta_handler(engine: DBEngine) -> Callable[[], Awaitable]:
    """Create a function that returns a dictionary of metadata related to a database.

    Args:
        engine: Database engine to pull metadata from.

    Returns:
        An async function that returns a dictionary of database metadata.
    """

    interface = create_model("Meta",
        dialect=(str, engine.dialect.name),
        driver=(str, engine.dialect.driver),
        database=(str, engine.url.database),
        host=(str | None, engine.url.host),
        port=(int | None, engine.url.port),
        username=(str | None, engine.url.username),
    )

    async def meta_handler() -> interface:
        return cast({
            "dialect": engine.dialect.name,
            "driver": engine.dialect.driver,
            "database": engine.url.database,
            "host": engine.url.host,
            "port": engine.url.port,
            "username": engine.url.username,
        }, interface)

    return meta_handler


def create_list_records_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable]:
    """Create a function that returns a list of records from the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function that returns a list of records from the given database model.
    """

    interface = create_db_interface(model)

    async def list_records(
        request: Request,
        response: Response,
        session: DBSession = Depends(create_session_iterator(engine)),
        pagination_params: dict[str, int] = Depends(get_pagination_params),
        ordering_params: dict[str, int] = Depends(get_ordering_params),
    ) -> list[interface]:
        """Fetch a list of records from the database.

        URL query parameters are used to enable filtering, ordering, and paginating returned values.
        """

        query = select(model)
        query = apply_pagination_params(query, pagination_params, response)
        query = apply_ordering_params(query, ordering_params, response)
        result = await execute_session_query(session, query)
        return cast(result.scalars().all(), list[interface])

    return list_records


def create_get_record_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable]:
    """Create a function for handling GET requests against a single record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function that returns a single record from the given database model.
    """

    interface = create_db_interface(model)

    async def get_record(
        request: Request,
        session: DBSession = Depends(create_session_iterator(engine)),
    ) -> interface:
        """Fetch a single record from the database."""

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)
        return get_record_or_404(result)

    return get_record


def create_post_record_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable]:
    """Create a function to handle POST requests for creating a new record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function to handle POST requests and create a new record.
    """

    interface = create_db_interface(model)

    async def post_record(
        request: Request,
        data: interface,
        session: DBSession = Depends(create_session_iterator(engine)),
    ) -> interface:
        """Create a new record in the database."""

        query = insert(model).values(**data.dict())
        result = await execute_session_query(session, query)
        await commit_session(session)
        return result.fetchone()

    return post_record


def create_put_record_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable]:
    """Create a function to handle PUT requests for updating a record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function to handle PUT requests and update a record.
    """

    interface = create_db_interface(model)

    async def put_record(
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
        return record

    return put_record


def create_patch_record_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable]:
    """Create a function to handle PATCH requests for partially updating a record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function to handle PATCH requests and partially update a record.
    """

    interface = create_db_interface(model)

    async def patch_record(
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
        return record

    return patch_record


def create_delete_record_handler(engine: DBEngine, model: DBModel) -> Callable[..., Awaitable]:
    """Create a function to handle DELETE requests for a single record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function to handle DELETE requests and delete a record.
    """

    async def delete_record(
        request: Request,
        session: DBSession = Depends(create_session_iterator(engine)),
    ) -> None:
        """Delete a single record from the database."""

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)

        record = get_record_or_404(result)
        await delete_session_record(session, record)
        await commit_session(session)

    return delete_record
