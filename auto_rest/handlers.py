"""Functions for handling incoming HTTP requests and generating responses."""

import logging

from fastapi import Depends
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from starlette.responses import Response

from .dependencies import *
from .metadata import VERSION
from .models import ModelBase

__all__ = [
    "create_list_handler",
    "create_meta_handler",
    "welcome_handler",
    "version_handler"
]

logger = logging.getLogger(__name__)


async def welcome_handler() -> dict:
    """Return a welcome message in JSON format pointing users to the docs."""

    return {"message": "Welcome to AutoRest! See the /docs/ endpoint to get started."}


async def version_handler() -> dict:
    """Return the application version number in JSON format."""

    return {"version": VERSION}


def create_meta_handler(conn_pool: Engine) -> callable:
    """Create a function that returns a dictionary of metadata related to a database.

    Args:
        conn_pool: A database connection pool to pull metadata from.

    Returns:
        An async function that returns a dictionary of database metadata.
    """

    async def meta_handler() -> dict:
        return {
            "dialect": conn_pool.dialect.name,
            "driver": conn_pool.dialect.driver,
            "database": conn_pool.url.database,
            "host": conn_pool.url.host,
            "port": conn_pool.url.port,
            "username": conn_pool.url.username,
        }

    return meta_handler


def create_list_handler(conn_pool: Engine, db_model: ModelBase) -> callable:
    """Create a function that returns a list of records from the given database model.

    Args:
        conn_pool: Connection pool to use for database interactions.
        db_model: The database ORM object to use for database manipulations.

    Returns:
        An async function that returns a list of records from the given database model.
    """

    async def list_handler(
        response: Response,
        db: Session = Depends(create_db_dependency(conn_pool)),
        pagination_params: dict[str, int] = Depends(get_pagination_params),
        ordering_params: dict[str, int] = Depends(get_ordering_params),
    ):
        logger.debug(f"Querying list of records from table '{db_model.__table__}'.")
        query = db.query(db_model)
        ordered_query = apply_ordering_params(query, db_model, ordering_params)
        items = ordered_query.all()

        return apply_pagination_params(items, pagination_params, response)

    return list_handler
