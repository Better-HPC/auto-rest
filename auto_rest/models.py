"""ORM layer used to dynamically map database schemas and generate model interfaces."""

import logging
from pathlib import Path

from sqlalchemy import create_engine, Engine, MetaData, URL
from sqlalchemy.orm import declarative_base

__all__ = [
    "create_connection_pool",
    "create_db_url",
    "create_db_models",
    "get_driver",
    "ModelBase",
]

logger = logging.getLogger(__name__)

ModelBase = declarative_base()


def get_driver(dbms: str) -> str:
    """Return the default driver to use for a given database type.

    Args:
        dbms: The type of database management system.

    Returns:
        The name of a SQLAlchemy driver.
    """

    return {
        "sqlite": "sqlite",
        "psql": "postgresql+asyncpg",
        "mysql": "mysql+asyncmy",
        "oracle": "oracle+oracledb",
        "mssql": "mssql+aiomysql"
    }[dbms]


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


def create_connection_pool(url: str, pool_size: int, max_overflow: int, pool_timeout: int) -> Engine:
    """Initialize a new pool of database connections.

    Args:
        url: Database connection URL.
        pool_size: Number of persistent connections to keep in the pool.
        max_overflow: Maximum connections to allow beyond the persistent pool size.
        pool_timeout: Maximum time to wait for a connection from the pool in seconds.

    Returns:
        A SQLAlchemy Engine instance.
    """

    params = {
        "pool_size": pool_size,
        "max_overflow": max_overflow,
        "pool_timeout": pool_timeout
    }

    params_str = ", ".join(f"{key}={value}" for key, value in params.items())
    logger.info(f"Connecting to database at {url} ({params_str}).")

    try:
        engine = create_engine(url, **params)
        logger.debug("Database connection established successfully.")
        return engine

    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise


def create_db_models(conn: Engine) -> dict[str, ModelBase]:
    """Dynamically generate database models.

    Args:
        conn: Open database connection.

    Returns:
        A dictionary mapping table names to database models
    """

    logger.info(f"Loading database schema for {conn.url}.")

    try:
        # Reflect the database schema from the database metadata
        metadata = MetaData()
        metadata.reflect(bind=conn)

        # Dynamically create a class for each table
        models = {}
        for table_name, table in metadata.tables.items():
            logger.debug(f"Building model for table {table_name}.")
            class_name = table_name.capitalize()
            models[table_name] = type(class_name, (ModelBase,), {"__table__": table})

        logger.info(f"Successfully generated {len(models)} models.")
        return models

    except Exception as e:  # pragma: no cover
        logger.error(f"Error generating models: {e}")
        raise
