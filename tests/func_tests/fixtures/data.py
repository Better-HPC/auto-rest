from datetime import date

from .schema import *

__all__ = ["FIXTURE_DATA"]

product1 = Product(name="Product A", description="Description of Product A", price=19.99, weight=1.5, discontinued=False)
product2 = Product(name="Product B", description="Description of Product B", price=29.99, weight=2.0, discontinued=True)

customer1 = Customer(name="Customer A", email="customerA@example.com", is_active=True, date_joined=date(2020, 1, 1))
customer2 = Customer(name="Customer B", email="customerB@example.com", is_active=True, date_joined=date(2021, 5, 15))

order1 = Order(customer_id=1, order_date=date(2022, 10, 10), shipping_date=date(2022, 10, 12), total_amount=49.98)
order2 = Order(customer_id=2, order_date=date(2022, 11, 20), shipping_date=date(2022, 11, 22), total_amount=59.97)

order_item1 = OrderItem(order_id=1, product_id=1, quantity=2, unit_price=19.99)
order_item2 = OrderItem(order_id=2, product_id=2, quantity=1, unit_price=29.99)

FIXTURE_DATA = [product1, product2, customer1, customer2, order1, order2, order_item1, order_item2]
