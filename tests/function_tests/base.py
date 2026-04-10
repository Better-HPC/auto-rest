"""Base classes for function tests against a live database and auto-rest server."""

import subprocess
import time
import unittest
from typing import ClassVar

import requests


class FunctionalTestBase(unittest.TestCase):
    """Base class for functional tests against a running auto-rest server.

    Subclasses must define `cli_args` with the full list of CLI arguments
    needed to launch auto-rest against their target database. The server
    is started once per test class (setUpClass) and torn down afterwards.
    """

    cli_args: ClassVar[list[str]] = []

    host: ClassVar[str] = "127.0.0.1"
    port: ClassVar[int] = 8081
    startup_timeout: ClassVar[int] = 30  # seconds

    _process: ClassVar[subprocess.Popen | None] = None

    @classmethod
    def base_url(cls) -> str:
        """The base url for the deployed auto-rest server."""

        return f"http://{cls.host}:{cls.port}"

    @classmethod
    def setUpClass(cls) -> None:
        """Start the auto-rest server before running tests."""

        cmd = ["auto-rest", f"--server-host={cls.host}", f"--server-port={cls.port}"] + cls.cli_args
        cls._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cls._wait_for_startup()

    @classmethod
    def tearDownClass(cls) -> None:
        """Shut down the auto-rest server after tests complete."""

        if cls._process:
            cls._process.terminate()
            try:
                cls._process.wait(timeout=10)

            except subprocess.TimeoutExpired:
                cls._process.kill()

    @classmethod
    def _wait_for_startup(cls) -> None:
        """Poll the server until it responds or the timeout is exceeded."""

        deadline = time.monotonic() + cls.startup_timeout
        while time.monotonic() < deadline:
            try:
                r = requests.get(cls.base_url() + "/", timeout=1)
                if r.status_code == 200:
                    return

            except requests.ConnectionError:
                pass

            time.sleep(0.5)

        cls._process.kill()
        raise RuntimeError(
            f"auto-rest did not start within {cls.startup_timeout}s. "
            f"stderr: {cls._process.stderr.read().decode()}")


class MetadataEndpointTests:
    """Function tests for metadata endpoints."""

    def test_welcome_endpoint(self) -> None:
        """Verify GET `/` returns a welcome message."""

        r = requests.get(self.base_url() + "/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("message", r.json())

    def test_meta_app_endpoint(self) -> None:
        """Verify GET `/meta/app/` returns name and version fields."""

        r = requests.get(self.base_url() + "/meta/app/")
        self.assertEqual(r.status_code, 200)

        body = r.json()
        self.assertIn("name", body)
        self.assertIn("version", body)

    def test_meta_engine_endpoint(self) -> None:
        """Verify GET `/meta/engine/` returns dialect, driver, and database fields."""

        r = requests.get(self.base_url() + "/meta/engine/")
        self.assertEqual(r.status_code, 200)

        body = r.json()
        self.assertIn("dialect", body)
        self.assertIn("driver", body)
        self.assertIn("database", body)

    def test_meta_schema_endpoint(self) -> None:
        """Verify GET `/meta/schema/` returns a tables object."""

        r = requests.get(self.base_url() + "/meta/schema/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("tables", r.json())
