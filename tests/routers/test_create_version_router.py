import unittest

from auto_rest.routers import create_version_router


class TestCreateVersionRouter(unittest.TestCase):
    """Unit tests for the `create_version_router` method."""

    def test_has_root_route(self) -> None:
        """Test the router supports GET requests against the root path."""

        router = create_version_router("1.2.3")
        routes = [(route.path, method) for route in router.routes for method in route.methods]

        expected_routes = [("/", "GET")]
        self.assertCountEqual(expected_routes, routes)
