"""Compatibility tests for SQLite databases."""

import tempfile
from unittest import TestCase

from auto_rest.models import get_driver
from .utils import AbstractCompatibilityTest


class SimpleTest(AbstractCompatibilityTest, TestCase):
    """Base compatibility tests applied to a SQLite database."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create a temporary SQLite file."""

        cls.temp_file = tempfile.NamedTemporaryFile(suffix='.sqlite')
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up temporary files."""

        cls.temp_file.close()
        super().tearDownClass()

    @classmethod
    def get_db_url(cls) -> str:
        """Return the URL of the database to test compatibility against."""

        driver = get_driver("sqlite")
        return f"{driver}:///{cls.temp_file.name}"
