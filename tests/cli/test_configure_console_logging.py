import logging
from unittest import TestCase

from auto_rest.cli import configure_console_logging


class TestConfigureCOnsoleLogging(TestCase):
    """Unit tests for the `configure_logging` function."""

    def test_log_level_is_set(self) -> None:
        """Test the logging level is configured."""

        for log_level_str in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            configure_console_logging(log_level_str)

            # The `getLevelName` method returns the numeric logging level when
            # passed the level name string. This was originally a bug, but is
            # an official feature as of Python 3.4.2
            log_level_int = logging.getLevelName(log_level_str)
            self.assertEqual(log_level_int, logging.getLogger().level)

    def test_log_format_is_set(self) -> None:
        """Test the logging format is configured."""

        configure_console_logging("INFO")
        handler = logging.getLogger().handlers[0]

        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertEqual(handler.formatter._fmt, "%(levelprefix)s %(message)s")

    def test_invalid_log_level(self) -> None:
        """Test an invalid logging level raises an error."""

        with self.assertRaisesRegex(ValueError, "Invalid logging level"):
            configure_console_logging("INVALID")
