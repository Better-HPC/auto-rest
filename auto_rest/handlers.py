"""Functions for handling incoming HTTP requests and generating responses."""

import logging

from fastapi import Depends, Response
from pydantic import create_model
from sqlalchemy import Engine, insert, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Session
from starlette.requests import Request

from .dist import version
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
    "version_handler",
    "welcome_handler",
]

logger = logging.getLogger(__name__)


async def welcome_handler() -> dict[str, str]:
    """Return a welcome message in JSON format pointing users to the docs."""

    return {"message": "Welcome to Auto-Rest!"}


async def version_handler() -> create_model("Version", version=(str, version)):
    """Return the application version number in JSON format."""

    return {"version": version}


def create_meta_handler(engine: Engine) -> callable:
    """Create a function that returns a dictionary of metadata related to a database.

    Args:
        engine: Database engine to pull metadata from.

    Returns:
        An async function that returns a dictionary of database metadata.
    """

    interface = create_model("Meta",
        dialect=(str, "postgresql"),
        driver=(str, "asyncpg"),
        database=(str, "default"),
        host=(str | None, "localhost"),
        port=(int | None, 5432),
        username=(str | None, "postgres"),
    )

    async def meta_handler() -> interface:
        return {
            "dialect": engine.dialect.name,
            "driver": engine.dialect.driver,
            "database": engine.url.database,
            "host": engine.url.host,
            "port": engine.url.port,
            "username": engine.url.username,
        }

    return meta_handler


def create_list_records_handler(engine: Engine | AsyncEngine, model: ModelBase) -> callable:
    """Create a function that returns a list of records from the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function that returns a list of records from the given database model.
    """

    async def list_records(
        request: Request,
        response: Response,
        session: Session | AsyncSession = Depends(create_session_factory(engine)),
        pagination_params: dict[str, int] = Depends(get_pagination_params),
        ordering_params: dict[str, int] = Depends(get_ordering_params),
    ) -> list[create_db_interface(model)]:
        """Fetch a list of records, applying filtering, pagination, and ordering parameters.

        Header values summarizing the applied operations are attached to the provided response object.
        
        Args:
            request: The incoming HTTP request.
            response: The outgoing HTTP response.
            session: The database session to use.
            pagination_params: Pagination parameters parsed from URL query params.
            ordering_params: Ordering parameters parsed from URL query params.
        """

        query = select(model)
        query = apply_pagination_params(query, pagination_params, response)
        query = apply_ordering_params(query, ordering_params, response)
        result = await execute_session_query(session, query)
        return result.scalars().all()

    return list_records


def create_get_record_handler(engine: Engine | AsyncEngine, model: ModelBase) -> callable:
    """Create a function for handling GET requests against a single record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function that returns a single record from the given database model.
    """

    async def get_record(
        request: Request,
        session: Session | AsyncSession = Depends(create_session_factory(engine)),
    ) -> create_db_interface(model):
        """Fetch a single record from the database.

        Path parameters from the incoming request are used as primary key values for
        the handled record.

        Args:
            request: The incoming HTTP request.
            session: The database session to use.

        Returns:
            The requested record values.
        """

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)
        return get_record_or_404(result)

    return get_record


def create_post_record_handler(engine: Engine | AsyncEngine, model: ModelBase) -> callable:
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
        session: Session | AsyncSession = Depends(create_session_factory(engine)),
    ) -> interface:
        """Create a new record in the database.
        
        Args:
            request: The incoming HTTP request.
            data: Key value pairs representing record field values.
            session: The database session to use.

        Returns:
            A copy of the new record values.
        """

        query = insert(model).values(**data.dict())
        result = await execute_session_query(session, query)
        await commit_session(session)
        return result.fetchone()

    return post_record


def create_put_record_handler(engine: Engine | AsyncEngine, model: ModelBase) -> callable:
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
        session: Session | AsyncSession = Depends(create_session_factory(engine)),
    ) -> interface:
        """Replace record values in the database with the provided data.

        Path parameters from the incoming request are used as primary key values for
        the handled record.
        
        Args:
            request: The incoming HTTP request.
            data: Key value pairs representing record field values.
            session: The database session to use.

        Returns:
            A copy of the new record values.
        """

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)

        record = get_record_or_404(result)
        for key, value in data.dict().items():
            setattr(record, key, value)

        await commit_session(session)
        return record

    return put_record


def create_patch_record_handler(engine: Engine | AsyncEngine, model: ModelBase) -> callable:
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
        session: Session | AsyncSession = Depends(create_session_factory(engine)),
    ) -> interface:
        """Update record values in the database with the provided data.

        Path parameters from the incoming request are used as primary key values for
        the handled record.

        Args:
            request: The incoming HTTP request.
            data: Key value pairs representing record field values.
            session: The database session to use.

        Returns:
            A copy of the new record values.
        """

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)

        record = get_record_or_404(result)
        for key, value in data.dict(exclude_unset=True).items():
            setattr(record, key, value)

        await commit_session(session)
        return record

    return patch_record


def create_delete_record_handler(engine: Engine | AsyncEngine, model: ModelBase) -> callable:
    """Create a function to handle DELETE requests for a single record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function to handle DELETE requests and delete a record.
    """

    async def delete_record(
        request: Request,
        session: Session | AsyncSession = Depends(create_session_factory(engine)),
    ) -> None:
        """Delete a single record from the database.

        Path parameters from the incoming request are used as primary key values for
        the handled record.

        Args:
            request: The incoming HTTP request.
            session: The database session to use.
        """

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)

        record = get_record_or_404(result)
        await delete_session_record(session, record)
        await commit_session(session)

    return delete_record
