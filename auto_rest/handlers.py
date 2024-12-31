"""Functions for handling incoming HTTP requests and generating responses."""

import logging

from fastapi import Depends, Response
from sqlalchemy import Engine, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status
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
    "welcome_handler",
    "version_handler"
]

logger = logging.getLogger(__name__)


async def welcome_handler():
    """Return a welcome message in JSON format pointing users to the docs."""

    return {"message": "Welcome to Auto-Rest!"}


async def version_handler():
    """Return the application version number in JSON format."""

    return {"version": version}


def create_meta_handler(engine: Engine) -> callable:
    """Create a function that returns a dictionary of metadata related to a database.

    Args:
        engine: Database engine to pull metadata from.

    Returns:
        An async function that returns a dictionary of database metadata.
    """

    async def meta_handler() -> dict:
        return {
            "dialect": engine.dialect.name,
            "driver": engine.dialect.driver,
            "database": engine.url.database,
            "host": engine.url.host,
            "port": engine.url.port,
            "username": engine.url.username,
        }

    return meta_handler


def create_list_records_handler(engine: Engine, model: ModelBase) -> callable:
    async def list_records(
        response: Response,
        session: Session | AsyncSession = Depends(create_session_factory(engine)),
        pagination_params: dict[str, int] = Depends(get_pagination_params),
        ordering_params: dict[str, int] = Depends(get_ordering_params),
    ) -> list[create_db_interface(model)]:

        query = select(model)
        query = apply_pagination_params(query, pagination_params, response)
        query = apply_ordering_params(query, ordering_params, response)
        result = await execute_session_query(session, query)
        return result.scalars().all()

    return list_records


def create_get_record_handler(engine: Engine, model: ModelBase) -> callable:
    """Create a function that returns a single records from the given database model.

    The returned record is identified by the primary key value(s) passed in
    the request path parameters. If the record is not found, a 404 error is raised.

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

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)
        return get_record_or_404(result)

    return get_record


def create_post_record_handler(engine: Engine, model: ModelBase) -> callable:
    """Create a function to handle POST requests for creating a new record in the database.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function to handle POST requests and create a new record.
    """

    interface = create_db_interface(model)

    async def post_record(
        response: Response,
        data: interface,
        session: Session | AsyncSession = Depends(create_session_factory(engine)),
    ) -> interface:

        query = insert(model).values(**data.dict())
        result = await execute_session_query(session, query)
        await commit_session(session)

        response.status_code = status.HTTP_201_CREATED
        return result.fetchone()

    return post_record


def create_put_record_handler(engine: Engine, model: ModelBase) -> callable:
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

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)

        record = get_record_or_404(result)
        for key, value in data.dict().items():
            setattr(record, key, value)

        await commit_session(session)
        return record

    return put_record


def create_patch_record_handler(engine: Engine, model: ModelBase) -> callable:
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

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)

        record = get_record_or_404(result)
        for key, value in data.dict(exclude_unset=True).items():
            setattr(record, key, value)

        await commit_session(session)
        return record

    return patch_record


def create_delete_record_handler(engine: Engine, model: ModelBase) -> callable:
    """Create a function to handle DELETE requests for deleting a record in the database.

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

        query = select(model).filter_by(**request.path_params)
        result = await execute_session_query(session, query)

        record = get_record_or_404(result)
        await delete_session_record(session, record)
        await commit_session(session)

    return delete_record
