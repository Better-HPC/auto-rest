"""Functional tests for each supported database type."""

import os

from tests.function_tests.base import FunctionalTestBase, MetadataEndpointTests


def _env(key: str, default: str) -> str:
    """Helper function for getting environment variables.

    Args:
        key: The environment variable name.
        default: The value to return if a variable is not set.
    """

    return os.environ.get(key, default)


class TestPostgreSQL(MetadataEndpointTests, FunctionalTestBase):
    """Functional tests against a PostgreSQL database."""

    port = 8082
    cli_args = [
        "--psql",
        f"--db-host={_env('FUNC_TEST_PG_HOST', '127.0.0.1')}",
        f"--db-port={_env('FUNC_TEST_PG_PORT', '5432')}",
        f"--db-name={_env('FUNC_TEST_PG_NAME', 'testdb')}",
        f"--db-user={_env('FUNC_TEST_PG_USER', 'postgres')}",
        f"--db-pass={_env('FUNC_TEST_PG_PASS', 'postgres')}",
    ]
