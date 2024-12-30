"""Functions for handling incoming HTTP requests and generating responses."""

import logging

from fastapi import Depends, HTTPException, Response
from sqlalchemy import Engine, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.requests import Request

from .dist import version
from .models import create_session_factory, ModelBase
from .utils import *

__all__ = [
    "create_get_record_handler",
    "create_list_records_handler",
    "create_meta_handler",
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
    """Create a function that returns a list of records from the given database model.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function that returns a list of records from the given database model.
    """

    async def list_records(
        response: Response,
        session: Session | AsyncSession = Depends(create_session_factory(engine)),
        pagination_params: dict[str, int] = Depends(get_pagination_params),
        ordering_params: dict[str, int] = Depends(get_ordering_params),
    ):
        query = select(model)
        query = apply_pagination_params(query, pagination_params, response)
        query = apply_ordering_params(query, ordering_params, response)

        if isinstance(session, AsyncSession):
            return (await session.execute(query)).scalars().all()

        return session.execute(query).scalars().all()

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
    ):

        query = select(model).filter_by(**request.path_params)
        if isinstance(session, AsyncSession):
            result = await session.execute(query)

        else:
            result = session.execute(query)

        if not (record := result.scalar_one_or_none()):
            raise HTTPException(status_code=404, detail="Record not found")

        return record

    return get_record
