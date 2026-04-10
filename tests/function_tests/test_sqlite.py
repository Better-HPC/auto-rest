"""Functional tests against a SQLite database."""

import os

from tests.function_tests.base import FunctionalTestBase, MetadataEndpointTests


class TestSQLite(MetadataEndpointTests, FunctionalTestBase):
    """Functional tests against a SQLite database."""

    _db_name = os.environ.get("FUNC_TEST_SL_NAME", "/tmp/auto_rest_test.db")

    port = 8081
    cli_args = [
        "--sqlite",
        f"--db-name={_db_name}",
    ]
