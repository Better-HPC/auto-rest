"""Functional tests against a MySQL database."""
import os

from tests.function_tests.base import FunctionalTestBase, MetadataEndpointTests


class TestMySQL(MetadataEndpointTests, FunctionalTestBase):
    """Functional tests against a MySQL database."""

    _my_host = os.environ.get("FUNC_TEST_MY_HOST", "127.0.0.1")
    _my_port = os.environ.get("FUNC_TEST_MY_PORT", "3306")
    _my_name = os.environ.get("FUNC_TEST_MY_NAME", "testdb")
    _my_user = os.environ.get("FUNC_TEST_MY_USER", "root")
    _my_pass = os.environ.get("FUNC_TEST_MY_PASS", "root")

    port = 8083
    cli_args = [
        "--mysql",
        f"--db-host={_my_host}",
        f"--db-port={_my_port}",
        f"--db-name={_my_name}",
        f"--db-user={_my_user}",
        f"--db-pass={_my_pass}",
    ]
