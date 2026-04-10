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


class TestSQLite(MetadataEndpointTests, FunctionalTestBase):
    """Functional tests against a SQLite database."""

    port = 8081
    cli_args = [
        "--sqlite",
        f"--db-name={_env('FUNC_TEST_DB_NAME', '/tmp/auto_rest_test.db')}",
    ]
