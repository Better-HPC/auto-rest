"""ORM layer using async SQLAlchemy to dynamically map database schemas and generate model interfaces."""

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
        host: The hostname or IP address of the database server.
        port: The port number for the database connection.
        database: The name of the database to connect to.
        username: The username to authenticate to the database.
        password: The password for the database user.

    Returns:
        The fully qualified database connection URL.
    """

    # Handle special case where SQLite uses file paths
    if driver == "sqlite" and host:
        path = Path(host)
        if path.is_absolute():
            return f"sqlite:///{path}"

        else:
            return f"sqlite:///{path}"

    return URL.create(
        drivername=driver,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database
    ).render_as_string(hide_password=False)


def create_db_engine(url: str, **kwargs) -> Engine | AsyncEngine:
    """Initialize a new pool of async database connections.

    Instantiates and returns an Engine or AsyncEngine depending on
    whether the underlying database driver supports async operations.

    Args:
        url: Database connection URL.
        **kwargs: Optional init parameters for the returned engine.

    Returns:
        A SQLAlchemy Engine instance.
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

    except Exception as e: # pragma: no cover
        logger.error(f"Could not connect to the database: {e}")
        raise


def create_db_metadata(conn: Engine | AsyncEngine) -> MetaData:
    """Create and reflect the metadata for the database connection.

    Args:
        conn: Open database connection (sync or async).

    Returns:
        A MetaData object reflecting the schema of the database.
    """

    logger.info(f"Loading database schema for {conn.url}.")

    try:
        metadata = MetaData()

        # For async engines, use an async reflection
        if isinstance(conn, AsyncEngine):
            loop = conn.sync_engine._pool._asyncio_event_loop
            loop.run_until_complete(metadata.reflect(bind=conn))

        # For sync engines, use the regular reflection
        else:
            metadata.reflect(bind=conn)

        return metadata

    except Exception as e:  # pragma: no cover
        logger.error(f"Error reflecting metadata: {e}")
        raise


def create_db_models(metadata: MetaData) -> dict[str, ModelBase]:
    """Dynamically generate database models from the provided metadata.

    Args:
        metadata: The schema of the database.

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
