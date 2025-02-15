import logging
from unittest import TestCase

from auto_rest.cli import configure_cli_logging


class TestConfigureCliLogging(TestCase):
    """Unit tests for the `configure_cli_logging` function."""

    def test_log_level_is_set(self) -> None:
        """Verify the logging level is configured to the correct level."""

        log_levels = (
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
            "debug",
            "info",
            "warning",
            "error",
            "critical",
        )

        for log_level_str in log_levels:

            # The `getLevelName` method returns the numeric logging level when
            # passed the level name string. This was originally a bug, but is
            # an official feature as of Python 3.4.2
            log_level_int = logging.getLevelName(log_level_str.upper())

            configure_cli_logging(log_level_str)
            self.assertEqual(log_level_int, logging.getLogger("auto_rest").level)
            self.assertEqual(log_level_int, logging.getLogger("auto_rest.access").level)

    def test_log_format_is_set(self) -> None:
        """Verify the logging format is customized."""

        configure_cli_logging("INFO")

        application_logger = logging.getLogger("auto_rest")
        access_logger = logging.getLogger("auto_rest.access")

        # Verify format of application logs
        self.assertEqual(1, len(application_logger.handlers))
        handler = application_logger.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertEqual(
            "%(log_color)s%(levelname)-8s%(reset)s (%(asctime)s) [%(correlation_id)s] %(message)s",
            handler.formatter._fmt
        )

        # Verify format of access logs
        self.assertEqual(1, len(access_logger.handlers))
        handler = access_logger.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertEqual(
            "%(log_color)s%(levelname)-8s%(reset)s (%(asctime)s) [%(correlation_id)s] %(ip)s:%(port)s - %(method)s %(endpoint)s - %(message)s",
            handler.formatter._fmt
        )

    def test_invalid_log_level(self) -> None:
        """Verify an invalid logging level raises an error."""

        with self.assertRaisesRegex(ValueError, "Invalid logging level"):
            configure_cli_logging("INVALID")
