"""Functions for handling incoming HTTP requests and generating responses."""

import logging

from fastapi import Depends
from sqlalchemy import Engine, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.responses import Response

from .utils import apply_ordering_params, apply_pagination_params, get_ordering_params, get_pagination_params
from .dist import version
from .models import create_session_factory, ModelBase

__all__ = [
    "create_list_handler",
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


def create_list_handler(engine: Engine, model: ModelBase) -> callable:
    """Create a function that returns a list of records from the given database model.

    Args:
        engine: Database engine to use when executing queries.
        model: The database ORM object to use for database manipulations.

    Returns:
        An async function that returns a list of records from the given database model.
    """

    async def list_handler(
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

    return list_handler
