"""Base classes for testing package compatibility against different database backends."""

from abc import ABCMeta, abstractmethod

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

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

    def test_print_tables_and_contents(self) -> None:
        """Test that prints the database tables and their contents."""

        # Query the metadata for tables in the database
        metadata = MetaData()
        metadata.reflect(bind=self.engine)

        # Print all tables
        print("Tables in the database:")
        for table_name in metadata.tables:
            print(f"- {table_name}")
