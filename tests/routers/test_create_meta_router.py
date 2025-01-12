from unittest import TestCase

from sqlalchemy import create_engine

from auto_rest.routers import create_meta_router


class TestCreateMetaRouter(TestCase):
    """Unit tests for the `create_meta_router` function."""

    def test_has_root_route(self) -> None:
        """Test the router supports GET requests against the root path."""

        engine = create_engine("sqlite:///:memory:")
        router = create_meta_router(engine)
        routes = [(route.path, method) for route in router.routes for method in route.methods]

        expected_routes = [("/", "GET")]
        self.assertCountEqual(expected_routes, routes)
