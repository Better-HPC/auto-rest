from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Column, INTEGER, MetaData, Table, VARCHAR

from auto_rest.handlers import create_schema_handler


class TestCreateSchemaHandler(TestCase):
    """Unit tests for the `create_schema_handler` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        cls.metadata = MetaData()
        Table("test_table1", cls.metadata, Column("col1", INTEGER, primary_key=True))
        Table("test_table2", cls.metadata, Column("col2", VARCHAR, default="foobar"))

        app = FastAPI()
        app.add_api_route("/", create_schema_handler(cls.metadata))
        cls.client = TestClient(app)

    def test_schema_handler(self) -> None:
        """Test the schema handler returns the correct database schema."""

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        schema = response.json().get("tables", {})

        # Check 'test_table1' columns and properties
        table1 = schema.get("test_table1", {})
        table1_columns = table1.get("columns", {})
        self.assertEqual("INTEGER", table1_columns["col1"]["type"])
        self.assertFalse(table1_columns["col1"]["nullable"])
        self.assertIsNone(table1_columns["col1"]["default"])

        # Check 'test_table2' columns and properties
        table2 = schema.get("test_table2", {})
        table2_columns = table2.get("columns", {})
        self.assertEqual("VARCHAR", table2_columns["col2"]["type"])
        self.assertTrue(table2_columns["col2"]["nullable"])
        self.assertEqual("foobar", table2_columns["col2"]["default"])
