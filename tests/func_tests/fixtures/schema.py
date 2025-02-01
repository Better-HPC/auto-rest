from datetime import date

from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base, relationship

__all__ = [
    "Customer",
    "Order",
    "OrderItem",
    "Product",
    "ModelBase",
]

ModelBase = declarative_base()


class Product(ModelBase):
    """Represents a product in a company catalog."""

    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    weight = Column(Float)
    discontinued = Column(Boolean, default=False)

    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")


class Order(ModelBase):
    """Represents a customer order."""

    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    order_date = Column(Date, default=date.today)
    shipping_date = Column(Date)
    total_amount = Column(Numeric(10, 2))

    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class Customer(ModelBase):
    """Represents a customer who places orders."""

    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    date_joined = Column(Date, default=date.today)

    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")


class OrderItem(ModelBase):
    """Represents an item in an order, linking products to orders."""

    __tablename__ = 'order_item'

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2))

    product = relationship("Product", back_populates="order_items")
    order = relationship("Order", back_populates="order_items")
