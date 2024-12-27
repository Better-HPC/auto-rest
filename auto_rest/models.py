"""Database utilities used to map database schemas and generate model interfaces."""

import asyncio
import logging
from pathlib import Path

from sqlalchemy import create_engine, Engine, MetaData, URL
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, Session, sessionmaker

__all__ = [
    "create_db_url",
    "create_db_engine",
    "create_db_metadata",
    "create_db_models",
    "create_session_factory",
    "ModelBase",
]

logger = logging.getLogger(__name__)
ModelBase = declarative_base()


def create_db_url(
    driver: str,
    host: str,
    port: int | None = None,
    database: str | None = None,
    username: str | None = None,
    password: str | None = None,
) -> URL:
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
        path = Path(host).resolve()
        return URL.create(drivername=driver, database=str(path))

    return URL.create(
        drivername=driver,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )


def create_db_engine(url: URL, **kwargs) -> Engine | AsyncEngine:
    """Initialize a new database engine.

    Instantiates and returns an `Engine` or `AsyncEngine` instance depending
    on whether the database URL uses a driver with support for async operations.

    Args:
        url: A fully qualified database URL.
        **kwargs: Optional init parameters for the returned instance.

    Returns:
        A SQLAlchemy `Engine` or `AsyncEngine` instance.
    """

    logger.info(f"Building database engine for {url}.")

    try:
        engine = create_async_engine(url, **kwargs)
        logger.debug("Asynchronous connection established.")
        return engine

    except InvalidRequestError as e:
        logger.warning(f"Async connection failed, falling back to sync. Error: {e}")

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


def create_db_metadata(engine: Engine | AsyncEngine) -> MetaData:
    """Create and reflect the metadata for the database connection.

    Args:
        engine: A database engine.

    Returns:
        A MetaData object reflecting the schema of the database.
    """

    logger.info(f"Loading database schema.")
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


def create_db_models(metadata: MetaData) -> dict[str, ModelBase]:
    """Dynamically generate database models from a metadata instance.

    Args:
        metadata: An up-to-date reflection of database metadata.

    Returns:
        A dictionary mapping table names to database models.
    """

    logger.info(f"Building database models.")
    models = {}

    try:
        # Dynamically create a class for each table
        for table_name, table in metadata.tables.items():
            logger.debug(f"Creating model for table {table_name}")
            models[table_name] = type(
                table_name.capitalize(),
                (ModelBase,),
                {"__table__": table},
            )

        logger.debug(f"Successfully generated {len(models)} models.")
        return models

    except Exception as e:  # pragma: no cover
        logger.error(f"Error generating models: {e}")
        raise


def create_session_factory(engine: Engine | AsyncEngine, autocommit: bool = False, autoflush: bool = False):
    """Create a factory function for generating database sessions.

    The returned function is suitable for use as a FastAPI dependency.

    Args:
        engine: Database engine to use when generating new sessions.
        autocommit: Whether to automatically commit changes to the database.
        autoflush: Whether to automatically flush changes to the database.

    Returns:
        A function that yields new database session.
    """

    if isinstance(engine, AsyncEngine):
        async_session_factory = async_sessionmaker(bind=engine, autocommit=autocommit, autoflush=autoflush)

        async def session_iterator() -> AsyncSession:
            async with async_session_factory() as session:
                yield session
    else:
        session_factory = sessionmaker(bind=engine, autocommit=autocommit, autoflush=autoflush)

        def session_iterator() -> Session:
            with session_factory() as session:
                yield session

    return session_iterator
