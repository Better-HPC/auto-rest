import unittest
from argparse import ArgumentError, ArgumentParser

from auto_rest.cli import create_argument_parser


class TestCreateArgumentParser(unittest.TestCase):
    """Unit tests for the `create_argument_parser` function."""

    def setUp(self) -> None:
        """Set up a new parser instance for each test."""

        self.parser: ArgumentParser = create_argument_parser(exit_on_error=False)

    def test_parser_name(self) -> None:
        """Test the parser is created with the correct name."""

        self.assertIsInstance(self.parser, ArgumentParser)
        self.assertEqual(self.parser.prog, "auto-rest")

    def test_default_log_level(self) -> None:
        """Test the default log level is INFO."""

        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertEqual(args.log_level, "INFO")

    def test_log_level_choices(self) -> None:
        """Test only valid log levels are accepted."""

        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        for level in valid_levels:
            args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--log-level", level])
            self.assertEqual(args.log_level, level)

        with self.assertRaises(ArgumentError):
            self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--log-level", "INVALID"])

    def test_server_defaults(self) -> None:
        """Test the default server settings."""

        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertEqual(args.server_host, "127.0.0.1")
        self.assertEqual(args.server_port, 8081)

    def test_pool_settings_defaults(self) -> None:
        """Test the default connection pool settings."""

        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertEqual(args.pool_min, None)
        self.assertEqual(args.pool_max, None)
        self.assertEqual(args.pool_out, None)
