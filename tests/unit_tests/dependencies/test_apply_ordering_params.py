import unittest

from sqlalchemy import Column, create_engine, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from auto_rest.dependencies import apply_ordering_params

Base = declarative_base()


class MockModel(Base):
    """A dummy database table to set up testing fixtures."""

    __tablename__ = "mock_table"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class TestApplyOrderingParams(unittest.TestCase):
    """Unit tests for the apply_ordering_params function."""

    @classmethod
    def setUpClass(cls):
        """Set up a temporary in-memory database and session."""

        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)

        cls.Session = sessionmaker(bind=cls.engine)
        cls.session = cls.Session()
        cls.session.add_all([
            MockModel(id=1, name="Bob"),
            MockModel(id=2, name="Alice"),
            MockModel(id=3, name="Charlie"),
        ])
        cls.session.commit()

    @classmethod
    def tearDownClass(cls):
        """Dispose of the database connection."""

        cls.session.close()
        cls.engine.dispose()

    def test_no_ordering_params(self) -> None:
        """Test when no ordering parameters are provided."""

        query = self.session.query(MockModel)
        ordered_query = apply_ordering_params(query, MockModel, {})
        self.assertEqual(query.all(), ordered_query.all())

    def test_valid_ordering_asc(self) -> None:
        """Test ordering by a valid column in ascending order."""

        query = self.session.query(MockModel)
        ordering_params = {"order_by": "name", "direction": "asc"}

        ordered_query = apply_ordering_params(query, MockModel, ordering_params)
        self.assertEqual(["Alice", "Bob", "Charlie"], [row.name for row in ordered_query.all()])

    def test_valid_ordering_desc(self) -> None:
        """Test ordering by a valid column in descending order."""

        query = self.session.query(MockModel)
        ordering_params = {"order_by": "name", "direction": "desc"}

        ordered_query = apply_ordering_params(query, MockModel, ordering_params)
        self.assertEqual(["Charlie", "Bob", "Alice"], [row.name for row in ordered_query.all()])

    def test_invalid_order_by_column(self):
        """Test ordering is ignored for an invalid column name."""

        query = self.session.query(MockModel)
        ordering_params = {"order_by": "invalid_column", "direction": "asc"}

        ordered_query = apply_ordering_params(query, MockModel, ordering_params)
        self.assertEqual(query.all(), ordered_query.all())

    def test_invalid_direction(self) -> None:
        """Test ordering defaults to ascending for an invalid direction."""

        query = self.session.query(MockModel)
        ordering_params = {"order_by": "name", "direction": "invalid"}

        ordered_query = apply_ordering_params(query, MockModel, ordering_params)
        self.assertEqual(["Alice", "Bob", "Charlie"], [row.name for row in ordered_query.all()], )
