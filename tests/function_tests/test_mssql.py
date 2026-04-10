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


class TestMSSQL(MetadataEndpointTests, FunctionalTestBase):
    """Functional tests against a Microsoft SQL Server database."""

    port = 8084
    cli_args = [
        "--mssql",
        f"--db-host={_env('FUNC_TEST_MS_HOST', '127.0.0.1')}",
        f"--db-port={_env('FUNC_TEST_MS_PORT', '1433')}",
        f"--db-name={_env('FUNC_TEST_MS_NAME', 'testdb')}",
        f"--db-user={_env('FUNC_TEST_MS_USER', 'sa')}",
        f"--db-pass={_env('FUNC_TEST_MS_PASS', 'Password123!')}",
    ]
