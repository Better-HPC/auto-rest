from unittest import TestCase

from sqlalchemy import create_engine, MetaData

from auto_rest.routers import create_meta_router


class TestCreateMetaRouter(TestCase):
    """Unit tests for the `create_meta_router` function."""

    def test_has_metadata_routes(self) -> None:
        """Test the router supports GET requests against the `version`, `engine`, and `schema` endpoints."""

        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()
        metadata.bind = engine
        version = "0.0.0"

        router = create_meta_router(engine, metadata, version)
        routes = [(route.path, method) for route in router.routes for method in route.methods]

        expected_routes = [
            ("/version", "GET"),
            ("/engine", "GET"),
            ("/schema", "GET"),
        ]

        self.assertCountEqual(expected_routes, routes)
