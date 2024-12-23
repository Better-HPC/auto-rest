from abc import ABCMeta, abstractmethod
from unittest import TestCase

from sqlalchemy import Column, create_engine, Integer, MetaData, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class TestModel(Base):
    __tablename__ = 'test_model'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class AbstractCompatibilityTest(metaclass=ABCMeta):
    """Base class for building database compatibility tests."""

    @classmethod
    @abstractmethod
    def get_db_url(cls) -> str:
        """Return the URL of the database to test compatibility against"""

    @classmethod
    def setUpClass(cls) -> None:
        """Instantiate a database engine."""

        db_url = cls.get_db_url()
        cls.engine = create_engine(db_url)
        cls.session_maker = sessionmaker(bind=cls.engine)

    def setUp(self) -> None:
        """Reset the database with new fixtures before each test."""

        # Drop all existing tables and recreate them
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        metadata.drop_all(bind=self.engine)
        metadata.create_all(bind=self.engine)

        # Create a session to add test data
        session = self.session_maker()

        # Add some simple test data
        test_data = [
            TestModel(name="Test Item 1"),
            TestModel(name="Test Item 2"),
            TestModel(name="Test Item 3")
        ]

        session.add_all(test_data)
        session.commit()


class SimpleTest(AbstractCompatibilityTest, TestCase):
    """Subclass that includes a simple test to print database tables and their contents."""

    @classmethod
    def get_db_url(cls) -> str:
        """Return the URL of the database to test compatibility against"""
        # For demonstration, use SQLite in-memory database
        return "sqlite:///:memory:"

    def test_print_tables_and_contents(self) -> None:
        """Test that prints the database tables and their contents."""
        # Query the metadata for tables in the database
        metadata = MetaData()
        metadata.reflect(bind=self.engine)

        # Print all tables
        print("Tables in the database:")
        for table_name in metadata.tables:
            print(f"- {table_name}")

        # Query and print contents of 'test_model' table
        session = self.session_maker()
        result = session.query(TestModel).all()

        print("\nContents of 'test_model' table:")
        for row in result:
            print(f"id: {row.id}, name: {row.name}")
