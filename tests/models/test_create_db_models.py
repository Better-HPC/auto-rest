import unittest

from sqlalchemy import Column, create_engine, INTEGER, MetaData, Table, VARCHAR

from auto_rest.models import create_db_models


class TestCreateDbModels(unittest.TestCase):
    """Unit tests for the `create_db_models` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up an in-memory SQLite database with test tables."""

        cls.engine = create_engine("sqlite:///:memory:")
        cls.metadata = MetaData()

        cls.test_table1 = Table(
            "test_table1",
            cls.metadata,
            Column("id", INTEGER, primary_key=True),
            Column("name", VARCHAR(50)),
        )

        cls.test_table2 = Table(
            "test_table2",
            cls.metadata,
            Column("id", INTEGER, primary_key=True),
            Column("description", VARCHAR(100)),
        )

        cls.metadata.create_all(cls.engine)

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up testing resources."""

        cls.engine.dispose()

    def test_models_are_created(self) -> None:
        """Test models are generated for each table."""

        models = create_db_models(self.engine)

        # Validate the count and names of generated models
        self.assertEqual(2, len(models))
        self.assertIn("test_table1", models)
        self.assertIn("test_table2", models)

        # Validate model names
        test_table1_model = models["test_table1"]
        self.assertTrue(hasattr(test_table1_model, "__table__"))
        self.assertEqual("test_table1", test_table1_model.__table__.name)

        test_table2_model = models["test_table2"]
        self.assertTrue(hasattr(test_table2_model, "__table__"))
        self.assertEqual("test_table2", test_table2_model.__table__.name)

        # Validate model columns (name and type)
        table1_columns = test_table1_model.__table__.columns
        self.assertCountEqual(["id", "name"], table1_columns.keys())
        self.assertEqual(INTEGER, table1_columns["id"].type.__class__)
        self.assertEqual(VARCHAR, table1_columns["name"].type.__class__)

        table2_columns = test_table2_model.__table__.columns
        self.assertCountEqual(["id", "description"], table2_columns.keys())
        self.assertEqual(INTEGER, table2_columns["id"].type.__class__)
        self.assertEqual(VARCHAR, table2_columns["description"].type.__class__)

    def test_create_db_models_empty_database(self) -> None:
        """Test handling an empty database."""

        empty_engine = create_engine("sqlite:///:memory:")
        models = create_db_models(empty_engine)

        # Validate that no models are generated
        self.assertEqual(0, len(models))
