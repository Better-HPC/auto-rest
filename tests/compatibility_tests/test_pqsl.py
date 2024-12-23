"""Compatibility tests for PostgreSQL databases."""

import os
from unittest import skipIf, TestCase

from auto_rest.models import create_db_url
from .utils import AbstractCompatibilityTest

PSQL_HOST = os.getenv("POSTGRES_HOST")


@skipIf(PSQL_HOST is None, "POSTGRES_HOST is not set")
class SimpleTest(AbstractCompatibilityTest, TestCase):
    """Base compatibility tests applied to a PostgreSQL database."""

    @classmethod
    def get_db_url(cls) -> str:
        """Return the URL of the database to test compatibility against."""

        return create_db_url(
            driver="postgresql+asyncpg",
            host=PSQL_HOST,
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB"),
            username=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
