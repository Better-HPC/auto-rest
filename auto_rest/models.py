"""Database utilities used to map database schemas and generate model interfaces."""

import asyncio
import logging
from pathlib import Path
from typing import Callable

import pydantic
from pydantic.main import ModelT
from sqlalchemy import create_engine, Engine, MetaData, URL
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, Session

__all__ = [
    "DBEngine",
    "DBModel",
    "DBSession",
    "create_db_engine",
    "create_db_interface",
    "create_db_metadata",
    "create_db_models",
    "create_db_url",
    "create_session_factory",
]

logger = logging.getLogger(__name__)

# Base classes and typing objects.
DBModel = declarative_base()
DBEngine = Engine | AsyncEngine
DBSession = Session | AsyncSession


def create_db_url(
    driver: str,
    database: str,
    host: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
) -> URL:
    """Create a database URL from the provided parameters.

    Args:
        driver: The SQLAlchemy-compatible database driver.
        database: The database name or file path (for SQLite).
        host: The database server hostname or IP address.
        port: The database server port number.
        username: The username for authentication.
        password: The password for the database user.

    Returns:
        A fully qualified database URL.
    """

    # Handle special case where SQLite uses file paths.
    if "sqlite" in driver:
        path = Path(database).resolve()
        return URL.create(drivername=driver, database=str(path))

    return URL.create(
        drivername=driver,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )


def create_db_engine(url: URL, **kwargs) -> DBEngine:
    """Initialize a new database engine.

    Instantiates and returns an `Engine` or `AsyncEngine` instance depending
    on whether the database URL uses a driver with support for async operations.

    Args:
        url: A fully qualified database URL.
        **kwargs: Optional init parameters for the engine instance.

    Returns:
        A SQLAlchemy `Engine` or `AsyncEngine` instance.
    """

    logger.info(f"Building database engine for {url}.")

    # Attempt to create an async engine by default.
    try:
        engine = create_async_engine(url, **kwargs)
        logger.debug("Asynchronous connection established.")
        return engine

    except InvalidRequestError as e:
        logger.warning(f"Async connection failed, falling back to sync. Error: {e}")

    # Fall back to a synchronous engine if async fails.
    try:
        engine = create_engine(url, **kwargs)
        logger.debug("Synchronous connection established.")
        return engine

    except Exception as e:  # pragma: no cover
        logger.error(f"Could not connect to the database: {e}")
        raise


async def _async_reflect_metadata(engine: AsyncEngine, metadata: MetaData) -> None:
    """Helper function used to reflect database metadata using an async engine."""

    async with engine.connect() as connection:
        await connection.run_sync(metadata.reflect)


def create_db_metadata(engine: DBEngine) -> MetaData:
    """Create and reflect metadata for the database connection.

    Args:
        engine: The database engine to use for reflection.

    Returns:
        A MetaData object reflecting the database schema.
    """

    logger.info("Loading database schema.")
    metadata = MetaData()

    try:
        if isinstance(engine, AsyncEngine):
            asyncio.run(_async_reflect_metadata(engine, metadata))

        else:
            metadata.reflect(bind=engine)

        return metadata

    except Exception as e:  # pragma: no cover
        logger.error(f"Schema reflection error: {e}")
        raise


def create_db_models(metadata: MetaData) -> dict[str, DBModel]:
    """Dynamically generate database models from a metadata instance.

    Args:
        metadata: A reflection of database metadata.

    Returns:
        A dictionary mapping table names to database models.
    """

    logger.info("Building database models.")
    models = {}

    try:
        # Dynamically create a class for each table.
        for table_name, table in metadata.tables.items():
            logger.debug(f"Creating model for table {table_name}")
            models[table_name] = type(
                table_name.capitalize(),
                (DBModel,),
                {"__table__": table},
            )

        logger.debug(f"Successfully generated {len(models)} models.")
        return models

    except Exception as e:  # pragma: no cover
        logger.error(f"Error generating models: {e}")
        raise


def create_db_interface(model: DBModel) -> type[ModelT]:
    """Create a Pydantic interface for a SQLAlchemy model.

    Args:
        model: A SQLAlchemy model to create an interface for.

    Returns:
        A Pydantic model class with the same structure as the provided SQLAlchemy model.
    """

    # Dynamic Pydantic models require a map of column names to their type and default value.
    columns = {col.name: (col.type.python_type, col.default) for col in model.__table__.columns}
    return pydantic.create_model(model.__name__, **columns)


def create_session_factory(engine: DBEngine) -> Callable[[], DBSession]:
    """Create a generator for database sessions.

    Args:
        engine: Database engine to use when generating new sessions.

    Returns:
        A function that yields new database sessions.
    """

    if isinstance(engine, AsyncEngine):
        async def session_iterator() -> AsyncSession:
            async with AsyncSession(bind=engine, autocommit=False, autoflush=True) as session:
                yield session
    else:
        async def session_iterator() -> Session:
            with Session(bind=engine, autocommit=False, autoflush=True) as session:
                yield session

    return session_iterator
