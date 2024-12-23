"""Base classes for testing package compatibility against different database backends."""

from abc import ABCMeta, abstractmethod

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auto_rest.app import create_app
from auto_rest.models import create_db_models
from .fixtures import *


class AbstractCompatibilityTest(metaclass=ABCMeta):
    """Base class for database compatibility tests."""

    @classmethod
    @abstractmethod
    def get_db_url(cls) -> str:
        """Return the URL of the database to test compatibility against."""

    @classmethod
    def setUpClass(cls) -> None:
        """Instantiate a database engine."""

        db_url = cls.get_db_url()
        cls.engine = create_engine(db_url)
        cls.session_maker = sessionmaker(bind=cls.engine)

    def setUp(self) -> None:
        """Reset the database with new fixtures before each test."""

        metadata.drop_all(bind=self.engine)
        metadata.create_all(bind=self.engine)
        with self.session_maker() as session:
            session.execute(users.insert().values(users_data))
            session.execute(products.insert().values(products_data))
            session.execute(orders.insert().values(orders_data))
            session.commit()

        models = create_db_models(self.engine)
        self.app = create_app(self.engine, models)
        self.client = TestClient(self.app)

    def test_list_endpoints(self) -> None:
        """Test fetching data from the list endpoints."""

        testing_endpoints = ['/db/users/', '/db/products/', '/db/orders/']
        testing_data = [users_data, products_data, orders_data]


        for endpoint, data in zip(testing_endpoints, testing_data):
            response = self.client.get(endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(data), len(response.json()))
