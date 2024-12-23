from unittest import TestCase

from tests.compatibility_tests.base import AbstractCompatibilityTest


class SimpleTest(AbstractCompatibilityTest, TestCase):
    """Subclass that includes a simple test to print database tables and their contents."""

    @classmethod
    def get_db_url(cls) -> str:
        """Return the URL of the database to test compatibility against."""

        return "sqlite:///:memory:"
