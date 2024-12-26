import logging
from unittest import TestCase

from auto_rest.app import configure_logging


class TestConfigureLogging(TestCase):
    """Unit tests for the `configure_logging` function."""

    def test_log_level_debug(self) -> None:
        """Test logging configuration for the DEBUG level."""

        configure_logging("DEBUG")
        self.assertEqual(logging.DEBUG, logging.getLogger().level)

    def test_log_level_info(self) -> None:
        """Test logging configuration for the INFO level."""

        configure_logging("INFO")
        self.assertEqual(logging.INFO, logging.getLogger().level)

    def test_log_level_warning(self) -> None:
        """Test logging configuration for the WARNING level."""

        configure_logging("WARNING")
        self.assertEqual(logging.WARNING, logging.getLogger().level)

    def test_log_level_error(self) -> None:
        """Test logging configuration for the ERROR level."""

        configure_logging("ERROR")
        self.assertEqual(logging.ERROR, logging.getLogger().level)

    def test_log_level_critical(self) -> None:
        """Test logging configuration for the CRITICAL level."""

        configure_logging("CRITICAL")
        self.assertEqual(logging.CRITICAL, logging.getLogger().level)

    def test_invalid_log_level(self) -> None:
        """Test an invalid logging level raises an error."""

        with self.assertRaisesRegex(ValueError, "Invalid logging level"):
            # noinspection PyTypeChecker
            configure_logging("INVALID")

    def test_log_format(self):
        """Test the logging format is configured."""

        configure_logging("INFO")
        handler = logging.getLogger().handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertEqual(handler.formatter._fmt, "%(levelprefix)s %(message)s")
