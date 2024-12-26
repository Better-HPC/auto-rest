"""Functions for handling incoming HTTP requests and generating responses."""

import logging

from fastapi import Depends
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from starlette.responses import Response

from .dependencies import *
from .dist import version
from .models import create_session_factory, ModelBase

__all__ = [
    "create_list_handler",
    "create_meta_handler",
    "welcome_handler",
    "version_handler"
]

logger = logging.getLogger(__name__)


async def welcome_handler() -> dict:
    """Return a welcome message in JSON format pointing users to the docs."""

    return {"message": "Welcome to Auto-Rest!"}


async def version_handler() -> dict:
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
        db: Session = Depends(create_session_factory(engine)),
        pagination_params: dict[str, int] = Depends(get_pagination_params),
        ordering_params: dict[str, int] = Depends(get_ordering_params),
    ):
        logger.debug(f"Querying list of records from table '{model.__table__}'.")
        query = db.query(model)
        ordered_query = apply_ordering_params(query, model, ordering_params)
        items = ordered_query.all()

        return apply_pagination_params(items, pagination_params, response)

    return list_handler
