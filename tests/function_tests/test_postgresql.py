"""Functional tests against a PostgreSQL database."""

import os

from tests.function_tests.base import FunctionalTestBase, MetadataEndpointTests


class TestPostgreSQL(MetadataEndpointTests, FunctionalTestBase):
    """Functional tests against a PostgreSQL database."""

    _pg_host = os.environ.get("FUNC_TEST_PG_HOST", "127.0.0.1")
    _pg_port = os.environ.get("FUNC_TEST_PG_PORT", "5432")
    _pg_name = os.environ.get("FUNC_TEST_PG_NAME", "testdb")
    _pg_user = os.environ.get("FUNC_TEST_PG_USER", "postgres")
    _pg_pass = os.environ.get("FUNC_TEST_PG_PASS", "postgres")

    port = 8082
    cli_args = [
        "--psql",
        f"--db-host={_pg_host}",
        f"--db-port={_pg_port}",
        f"--db-name={_pg_name}",
        f"--db-user={_pg_user}",
        f"--db-pass={_pg_pass}",
    ]
