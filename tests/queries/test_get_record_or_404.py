from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from fastapi import HTTPException, status

from auto_rest.queries import get_record_or_404


class TestGetRecordOr404(IsolatedAsyncioTestCase):
    """Unit tests for the `get_record_or_404` function."""

    def test_get_record_found(self) -> None:
        """Test retrieving a record when it exists."""

        # Create a mock result where scalar_one_or_none() returns a valid record
        mock_result = MagicMock()
        mock_record = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_record

        # Call the function and assert the returned record is the mock record
        result = get_record_or_404(mock_result)
        self.assertEqual(result, mock_record)

    def test_get_record_not_found(self) -> None:
        """Test raising a 404 error when no record is found."""

        # Create a mock result where scalar_one_or_none() returns None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        # Verify a 404 error is raised
        with self.assertRaises(HTTPException) as context:
            get_record_or_404(mock_result)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, "Record not found")
