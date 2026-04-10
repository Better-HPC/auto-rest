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



class TestMySQL(MetadataEndpointTests, FunctionalTestBase):
    """Functional tests against a MySQL database."""

    port = 8083
    cli_args = [
        "--mysql",
        f"--db-host={_env('FUNC_TEST_MY_HOST', '127.0.0.1')}",
        f"--db-port={_env('FUNC_TEST_MY_PORT', '3306')}",
        f"--db-name={_env('FUNC_TEST_MY_NAME', 'testdb')}",
        f"--db-user={_env('FUNC_TEST_MY_USER', 'root')}",
        f"--db-pass={_env('FUNC_TEST_MY_PASS', 'root')}",
    ]

