from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from auto_rest.models import parse_db_settings


class TestCreateDbEngine(TestCase):
    """Unit tests for the `parse_db_settings` method."""

    def test_valid_file(self) -> None:
        """Verify valid YAML files are parsed and returned."""

        with NamedTemporaryFile(delete=False, mode='w') as temp_file:
            temp_file.write("key: value")
            temp_file_path = Path(temp_file.name)

        expected_output = {"key": "value"}
        result = parse_db_settings(temp_file_path)
        self.assertEqual(result, expected_output)

    def test_empty_file(self) -> None:
        """Verify an empty dictionary is returned when the file is empty."""

        with NamedTemporaryFile(delete=False, mode='w') as temp_file:
            temp_file.write("")
            temp_file_path = Path(temp_file.name)

        expected_output = {}
        result = parse_db_settings(temp_file_path)
        self.assertEqual(result, expected_output)

    def test_file_not_found(self) -> None:
        """Verify a `FileNotFoundError` error is raised for missing files."""

        with self.assertRaises(FileNotFoundError):
            parse_db_settings(Path("non_existent_file.yaml"))

    def test_no_file_specified(self) -> None:
        """Verify an empty dictionary is returned when no file is specified."""

        result = parse_db_settings(None)
        self.assertEqual(result, {})
