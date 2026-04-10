"""Functional tests against a Microsoft SQL Server database."""

import os

from tests.function_tests.base import FunctionalTestBase, MetadataEndpointTests


class TestMSSQL(MetadataEndpointTests, FunctionalTestBase):
    """Functional tests against a Microsoft SQL Server database."""

    _ms_host = os.environ.get("FUNC_TEST_MS_HOST", "127.0.0.1")
    _ms_port = os.environ.get("FUNC_TEST_MS_PORT", "1433")
    _ms_name = os.environ.get("FUNC_TEST_MS_NAME", "testdb")
    _ms_user = os.environ.get("FUNC_TEST_MS_USER", "sa")
    _ms_pass = os.environ.get("FUNC_TEST_MS_PASS", "Password123!")

    port = 8084
    cli_args = [
        "--mssql",
        f"--db-host={_ms_host}",
        f"--db-port={_ms_port}",
        f"--db-name={_ms_name}",
        f"--db-user={_ms_user}",
        f"--db-pass={_ms_pass}",
    ]
