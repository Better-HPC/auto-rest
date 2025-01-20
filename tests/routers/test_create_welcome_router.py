from unittest import TestCase

from auto_rest.routers import create_welcome_router


class TestCreateWelcomeRouter(TestCase):
    """Unit tests for the `create_welcome_router` method."""

    def test_has_root_route(self) -> None:
        """Verify the router supports GET requests against the root path."""

        router = create_welcome_router()
        routes = [(route.path, method) for route in router.routes for method in route.methods]

        expected_routes = [("/", "GET")]
        self.assertCountEqual(expected_routes, routes)
