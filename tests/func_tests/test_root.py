from tests.func_tests.fixtures import FunctionTestingBase


class RootEndpoint(FunctionTestingBase):
    """Function tests for the root API endpoint."""

    def test_get_returns_welcome_message(self) -> None:
        """Verify the root endpoint returns a welcome message."""

        response = self.http_session.get(self.server_url)
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json()["message"])

    def test_write_operations_return_405(self) -> None:
        """Verify write operations against the root endpoint return a 405 error."""

        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            response = self.http_session.request(method, self.server_url)
            self.assertEqual(405, response.status_code)
