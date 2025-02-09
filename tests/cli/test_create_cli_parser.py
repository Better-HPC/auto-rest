from argparse import ArgumentError
from pathlib import Path
from unittest import TestCase

from auto_rest.cli import create_cli_parser, VERSION


class TestCreateCliParser(TestCase):
    """Unit tests for the `create_cli_parser` function.

    Individual methods target behavior for a different subset of commandline arguments.
    """

    def setUp(self) -> None:
        """Set up a new parser instance for each test."""

        self.parser = create_cli_parser(exit_on_error=False)

    def test_parser_name(self) -> None:
        """Verify the parser is created with the correct program name."""

        self.assertEqual("auto-rest", self.parser.prog)

    def test_log_level(self) -> None:
        """Verify the `--log-level` argument stores valid logging levels."""

        # Validate the default log level
        args = self.parser.parse_args(["--sqlite", "--db-name", "default"])
        self.assertEqual("INFO", args.log_level)

        # Test valid logging levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        for level in valid_levels:
            args = self.parser.parse_args(["--sqlite", "--db-name", "default", "--log-level", level])
            self.assertEqual(level, args.log_level)

        # Test lower case levels
        for level in valid_levels:
            args = self.parser.parse_args(["--sqlite", "--db-name", "default", "--log-level", level.lower()])
            self.assertEqual(level, args.log_level)

        # Test an invalid logging level
        with self.assertRaises(ArgumentError):
            self.parser.parse_args(["--sqlite", "--db-name", "default", "--log-level", "INVALID"])

    def test_db_driver(self) -> None:
        """Verify the database driver arguments store their state."""

        # Map CLI flags to expected database drivers
        db_drivers = {
            "sqlite": "sqlite+aiosqlite",
            "psql": "postgresql+asyncpg",
            "mysql": "mysql+asyncmy",
            "oracle": "oracle+oracledb",
            "mssql": "mssql+aiomysql",
        }

        # Test built in drivers
        for flag, driver in db_drivers.items():
            args = self.parser.parse_args([f"--{flag}", "--db-name", "default"])
            self.assertEqual(driver, args.db_driver)

        # Test a custom driver
        args = self.parser.parse_args(["--driver", "custom-driver", "--db-name", "default"])
        self.assertEqual("custom-driver", args.db_driver)

    def test_db_settings(self) -> None:
        """Verify database-connection arguments and default values."""

        # Test default values
        default_args = self.parser.parse_args(["--sqlite", "--db-name", "default"])
        self.assertEqual("default", default_args.db_name)
        self.assertIsNone(default_args.db_port)
        self.assertIsNone(default_args.db_config)

        # Test parsing custom values
        config_path = Path("/path/to/db-config.yaml")
        custom_args = self.parser.parse_args([
            "--psql",
            "--db-host", "localhost",
            "--db-name", "default",
            "--db-user", "user",
            "--db-pass", "password",
            "--db-config", str(config_path)
        ])

        self.assertEqual("localhost", custom_args.db_host)
        self.assertEqual("user", custom_args.db_user)
        self.assertEqual("password", custom_args.db_pass)
        self.assertEqual(config_path, custom_args.db_config)

    def test_server_settings(self) -> None:
        """Verify server-related settings and default values."""

        # Test default values
        default_args = self.parser.parse_args(["--sqlite", "--db-name", "default"])
        self.assertEqual("127.0.0.1", default_args.server_host)
        self.assertEqual(8081, default_args.server_port)

        # Test parsing custom values
        custom_args = self.parser.parse_args([
            "--sqlite",
            "--db-name", "default",
            "--db-host", "localhost",
            "--server-host", "0.0.0.0",
            "--server-port", "9090",
        ])

        self.assertEqual("0.0.0.0", custom_args.server_host)
        self.assertEqual(9090, custom_args.server_port)

    def test_app_settings(self) -> None:
        """Verify app-settings related arguments and default values."""

        # Test default values
        default_args = self.parser.parse_args(["--sqlite", "--db-name", "default"])
        self.assertEqual("Auto-REST", default_args.app_title)
        self.assertEqual(VERSION, default_args.app_version)

        # Test parsing custom values
        custom_args = self.parser.parse_args([
            "--sqlite",
            "--db-name", "default",
            "--app-title", "Custom API",
            "--app-version", "1.2.3",
        ])

        self.assertEqual("Custom API", custom_args.app_title)
        self.assertEqual("1.2.3", custom_args.app_version)
