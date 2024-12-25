"""ORM layer using async SQLAlchemy to dynamically map database schemas and generate model interfaces."""

import asyncio
import logging
from pathlib import Path

from sqlalchemy import create_engine, Engine, MetaData, URL
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import declarative_base

__all__ = [
    "create_db_engine",
    "create_db_metadata",
    "create_db_models",
    "create_db_url",
    "ModelBase"
]

logger = logging.getLogger(__name__)

ModelBase = declarative_base()


def create_db_url(
    driver: str,
    host: str,
    port: int | None = None,
    database: str | None = None,
    username: str | None = None,
    password: str | None = None
) -> str:
    """Create a database URL from the provided parameters.

    Args:
        driver: The sqlalchemy compatible database driver.
        host: The database server hostname or IP address.
        port: The database server port number.
        database: The database name.
        username: The username to authenticate as.
        password: The password for the database user.

    Returns:
        The fully qualified database URL.
    """

    # Handle special case where SQLite uses file paths
    if "sqlite" in driver:
        path = Path(host)
        if path.is_absolute():
            return f"{driver}:///{path}"

        else:
            return f"{driver}:///{path}"

    return URL.create(
        drivername=driver,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database
    ).render_as_string(hide_password=False)


def create_db_engine(url: str, **kwargs) -> Engine | AsyncEngine:
    """Initialize a new database engine.

    Instantiates and returns an `Engine` or `AsyncEngine` instance depending
    on whether the database URL indicates support for async operations.

    Args:
        url: A fully qualified database connection URL.
        **kwargs: Optional init parameters for the returned instance.

    Returns:
        A SQLAlchemy `Engine` or `AsyncEngine` instance.
    """

    params_str = ", ".join(f"{key}={value}" for key, value in kwargs.items())
    logger.info(f"Connecting to database at {url} ({params_str}).")

    try:
        engine = create_async_engine(url, **kwargs)
        logger.debug("Asynchronous database connection established successfully.")
        return engine

    except InvalidRequestError as e:
        logger.warning(f"Could not establish asynchronous connection. Falling back to synchronous. ({e})")

    try:
        engine = create_engine(url, **kwargs)
        logger.debug("Synchronous database connection established successfully.")
        return engine

    except Exception as e:  # pragma: no cover
        logger.error(f"Could not connect to the database: {e}")
        raise


async def _async_reflect_metadata(engine: AsyncEngine, metadata: MetaData) -> None:
    """Helper function used to reflect database metadata using an async engine."""

    async with engine.connect() as connection:
        await connection.run_sync(metadata.reflect)


def create_db_metadata(engine: Engine | AsyncEngine) -> MetaData:
    """Create and reflect the metadata for the database connection.

    Args:
        engine: A database engine.

    Returns:
        A MetaData object reflecting the schema of the database.
    """

    logger.info(f"Loading database schema for {engine.url}.")

    try:
        metadata = MetaData()

        if isinstance(engine, AsyncEngine):
            asyncio.run(_async_reflect_metadata(engine, metadata))

        else:
            metadata.reflect(bind=engine)

        return metadata

    except Exception as e:  # pragma: no cover
        logger.error(f"Error mapping database schema: {e}")
        raise


def create_db_models(metadata: MetaData) -> dict[str, ModelBase]:
    """Dynamically generate database models from the provided metadata.

    Args:
        metadata: Up-to-date database metadata.

    Returns:
        A dictionary mapping table names to database models.
    """

    models = {}

    try:
        # Dynamically create a class for each table
        for table_name, table in metadata.tables.items():
            logger.debug(f"Building model for table {table_name}.")
            class_name = table_name.capitalize()
            models[table_name] = type(class_name, (ModelBase,), {"__table__": table})

        logger.info(f"Successfully generated {len(models)} models.")
        return models

    except Exception as e:  # pragma: no cover
        logger.error(f"Error generating models: {e}")
        raise
