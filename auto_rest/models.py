"""
The `models` module facilitates communication with relational databases
via dynamically generated object relational mappers (ORMs). Building
on the popular SQLAlchemy package, it natively supports multiple
Database Management Systems (DBMS) without requiring custom configuration
or setup.

!!! example "Example: Creating ORM objects"

    Utility functions are provided for connecting to the database,
    mapping the schema, and dynamically generating ORM models based on
    the existing database structure.

    ```python
    connection_args = dict(...)
    db_url = create_db_url(**connection_args)
    db_conn = create_db_engine(db_url)
    db_meta = create_db_metadata(db_conn)
    db_models = create_db_models(db_meta)
    ```

Support for asynchronous operations is automatically determined based on
the chosen database. If the driver supports asynchronous operations, the
connection and session handling are configured accordingly.

!!! important "Developer Note"

    When working with database objects, the returned object type may vary
    depending on whether the underlying driver is synchronous or asynchronous.
    Of particular note are database engines (`Engine` / `AsyncEngine`) and
    sessions (`Session` / `AsyncSession`).
"""

import asyncio
import logging
from pathlib import Path
from typing import Callable

from pydantic.main import create_model, ModelT
from sqlalchemy import create_engine, Engine, MetaData, URL
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
    "create_session_iterator",
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

    logger.debug("Resolving database URL.")

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


def create_db_engine(url: URL) -> DBEngine:
    """Initialize a new database engine.

    Instantiates and returns an `Engine` or `AsyncEngine` instance depending
    on whether the database URL uses a driver with support for async operations.

    Args:
        url: A fully qualified database URL.

    Returns:
        A SQLAlchemy `Engine` or `AsyncEngine` instance.
    """

    logger.debug(f"Building database engine for {url}.")

    if url.get_dialect().is_async:
        engine = create_async_engine(url)
        logger.debug("Asynchronous connection established.")
        return engine

    else:
        engine = create_engine(url)
        logger.debug("Synchronous connection established.")
        return engine


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

    logger.debug("Loading database metadata.")
    metadata = MetaData()

    if isinstance(engine, AsyncEngine):
        asyncio.run(_async_reflect_metadata(engine, metadata))

    else:
        metadata.reflect(bind=engine)

    return metadata


def create_db_models(metadata: MetaData) -> dict[str, DBModel]:
    """Dynamically generate database models from a metadata instance.

    Args:
        metadata: A reflection of database metadata.

    Returns:
        A dictionary mapping table names to database models.
    """

    logger.debug("Building database models...")
    models = {}

    # Dynamically create a class for each table.
    for table_name, table in metadata.tables.items():
        logger.debug(f"> Creating model for table {table_name}.")
        models[table_name] = type(
            table_name.capitalize(),
            (DBModel,),
            {"__table__": table},
        )

    logger.debug(f"Successfully generated {len(models)} models.")
    return models


def create_db_interface(model: DBModel) -> type[ModelT]:
    """Create a Pydantic interface for a SQLAlchemy model.

    Args:
        model: A SQLAlchemy model to create an interface for.

    Returns:
        A Pydantic model class with the same structure as the provided SQLAlchemy model.
    """

    fields = {
        col.name: (col.type.python_type, col.default if col.default is not None else ...)
        for col in model.__table__.columns
    }

    return create_model(model.__name__, **fields)


def create_session_iterator(engine: DBEngine) -> Callable[[], DBSession]:
    """Create a generator for database sessions.

    Returns a synchronous or asynchronous function depending on whether
    the database engine supports async operations. The type of session
    returned also depends on the underlying database engine, and will
    either be a `Session` or `AsyncSession` instance.

    Args:
        engine: Database engine to use when generating new sessions.

    Returns:
        A function that yields a single new database session.
    """

    if isinstance(engine, AsyncEngine):
        async def session_iterator() -> AsyncSession:
            async with AsyncSession(bind=engine, autocommit=False, autoflush=True) as session:
                yield session

    else:
        def session_iterator() -> Session:
            with Session(bind=engine, autocommit=False, autoflush=True) as session:
                yield session

    return session_iterator
