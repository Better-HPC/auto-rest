"""Compatibility tests for SQLite databases."""

from unittest import TestCase

from tests.compatibility_tests.base import AbstractCompatibilityTest


class SimpleTest(AbstractCompatibilityTest, TestCase):
    """Base compatibility tests applied to a SQLite database."""

    @classmethod
    def get_db_url(cls) -> str:
        """Return the URL of the database to test compatibility against."""

        return "sqlite:///:memory:"
