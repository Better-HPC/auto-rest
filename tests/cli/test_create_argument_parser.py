from argparse import ArgumentError, ArgumentParser
from unittest import TestCase

from auto_rest.cli import create_argument_parser


class TestCreateArgumentParser(TestCase):
    """Unit tests for the `create_argument_parser` function."""

    def setUp(self) -> None:
        """Set up a new parser instance for each test."""

        self.parser = create_argument_parser(exit_on_error=False)

    def test_parser_name(self) -> None:
        """Test the parser is created with the correct program name."""

        self.assertIsInstance(self.parser, ArgumentParser)
        self.assertEqual(self.parser.prog, "auto-rest")

    def test_log_level(self) -> None:
        """Test only valid log levels are accepted and default value is correct."""

        # Validate the default log level
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertEqual(args.log_level, "INFO")

        # Test valid logging levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        for level in valid_levels:
            args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--log-level", level])
            self.assertEqual(args.log_level, level)

        # Test an invalid logging level
        with self.assertRaises(ArgumentError):
            self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--log-level", "INVALID"])

    def test_db_driver_selection(self) -> None:
        """Test mutually exclusive arguments for database driver selection."""

        # Test valid database driver options
        cli_flags = ["sqlite", "psql", "mysql", "oracle", "mssql"]
        db_drivers = ["sqlite", "postgresql+asyncpg", "mysql+asyncmy", "oracle+oracledb", "mssql+aiomysql"]

        for flag, driver in zip(cli_flags, db_drivers):
            args = self.parser.parse_args([f"--{flag}", "--db-host", "localhost"])
            self.assertEqual(args.db_driver, driver)

        # Test custom driver
        args = self.parser.parse_args(["--driver", "custom-driver", "--db-host", "localhost"])
        self.assertEqual(args.db_driver, "custom-driver")

    def test_db_settings(self) -> None:
        """Test the database-related arguments and default values."""

        # Test required database host
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertEqual(args.db_host, "localhost")

        # Test default database port
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertEqual(args.db_port, None)

        # Test optional db-name, user, and password
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--db-name", "testdb", "--db-user", "user", "--db-pass", "password"])
        self.assertEqual(args.db_name, "testdb")
        self.assertEqual(args.db_user, "user")
        self.assertEqual(args.db_pass, "password")

    def test_pool_settings(self) -> None:
        """Test the database connection pool settings and defaults."""

        # Test default pool settings (None should be default)
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertIsNone(args.pool_min)
        self.assertIsNone(args.pool_max)
        self.assertIsNone(args.pool_out)

        # Test valid pool settings
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--pool-min", "5", "--pool-max", "20", "--pool-out", "30"])
        self.assertEqual(args.pool_min, 5)
        self.assertEqual(args.pool_max, 20)
        self.assertEqual(args.pool_out, 30)

    def test_enabled_docs_flag(self) -> None:
        """Test the `--enable-docs` flag behavior."""

        # Default should be False
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertFalse(args.enable_docs)

        # Test enabling docs
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--enable-docs"])
        self.assertTrue(args.enable_docs)

    def test_enabled_meta_flag(self) -> None:
        """Test the `--enable-meta` flag behavior."""

        # Default should be False
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertFalse(args.enable_meta)

        # Test enabling meta
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--enable-meta"])
        self.assertTrue(args.enable_meta)

    def test_server_settings(self) -> None:
        """Test server-related settings with default values."""

        # Test default server host and port
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertEqual(args.server_host, "127.0.0.1")
        self.assertEqual(args.server_port, 8081)

        # Test custom server host and port
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--server-host", "0.0.0.0", "--server-port", "9090"])
        self.assertEqual(args.server_host, "0.0.0.0")
        self.assertEqual(args.server_port, 9090)
