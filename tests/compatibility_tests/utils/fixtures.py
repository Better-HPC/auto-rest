"""Table schemas and associated dummy data used in testing."""

from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, MetaData, String, Table

__all__ = [
    "metadata",
    "products",
    "products_data",
    "orders",
    "orders_data",
    "users",
    "users_data",
]

metadata = MetaData()

users = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("email", String, nullable=False, unique=True),
    Column("age", Integer, nullable=True),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime, default=datetime.now)
)

users_data = [
    {"id": 1, "name": "John Doe", "email": "john.doe@example.com", "age": 30},
    {"id": 2, "name": "Jane Smith", "email": "jane.smith@example.com", "age": 25, "is_active": False},
    {"id": 3, "name": "Alice Johnson", "email": "alice.johnson@example.com", "age": 28}
]

products = Table("products", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("price", Float, nullable=False, default=0.0)
)

products_data = [
    {"id": 1, "name": "Laptop", "price": 1200.00},
    {"id": 2, "name": "Smartphone", "price": 800.00},
    {"id": 3, "name": "Headphones", "price": 150.00}
]

orders = Table("orders", metadata,
    Column("user_id", Integer, primary_key=True),
    Column("product_id", Integer, primary_key=True),
    Column("amount", Float, nullable=False),
    Column("order_date", Date, nullable=False)
)

orders_data = [
    {"user_id": 1, "product_id": 1, "amount": 1200.00, "order_date": datetime(2024, 12, 1)},
    {"user_id": 2, "product_id": 2, "amount": 800.00, "order_date": datetime(2024, 12, 2)},
    {"user_id": 3, "product_id": 3, "amount": 150.00, "order_date": datetime(2024, 12, 3)}
]
