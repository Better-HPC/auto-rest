"""Functional tests for each supported database type.

Each class wires up the CLI args for its database. The shared test logic
lives in AutoRestMetadataEndpointTests, FunctionalTestBase. Add DB-specific tests here by
overriding or extending within the relevant class.

Environment variables used (all have defaults for local dev):
    FUNC_TEST_DB_NAME   - database name / SQLite file path
    FUNC_TEST_DB_HOST   - database host
    FUNC_TEST_DB_PORT   - database port (int)
    FUNC_TEST_DB_USER   - database username
    FUNC_TEST_DB_PASS   - database password
"""

import os

from .base import FunctionalTestBase, MetadataEndpointTests


def _env(key: str, default: str) -> str:
    return os.environ.get(key, default)


class TestSQLite(MetadataEndpointTests, FunctionalTestBase):
    """Functional tests against a SQLite database."""

    port = 8081
    cli_args = [
        "--sqlite",
        f"--db-name={_env('FUNC_TEST_DB_NAME', '/tmp/auto_rest_test.db')}",
    ]


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
