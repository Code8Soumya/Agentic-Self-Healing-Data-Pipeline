"""Generates realistic e-commerce order events.

CONNECTIONS:
- Imports: app.models.events.OrderEventV1, app.models.events.ShippingAddress
- Called by: generator.py (orchestrator) to produce order events
- Output: Published to Pub/Sub 'raw-ecommerce-events' topic via generator.py
- Events flow: This -> Pub/Sub -> Dataflow (Beam) -> BigQuery

DATA DOMAIN:
- Product categories: electronics, clothing, home, books, sports
- Payment methods: credit_card, upi, cod, debit_card
- Currencies: INR, USD, EUR
- Cities: Mumbai, Delhi, Bangalore, Chennai, Hyderabad, Pune, Kolkata
- Statuses: placed, confirmed, shipped, delivered
"""
import random
from datetime import datetime
from app.models.events import OrderEventV1, ShippingAddress

# ── Data Domain Constants ──
PRODUCT_CATALOG = [
    {"id": "PROD-00001", "name": "Wireless Earbuds", "category": "electronics", "price": 2499.00},
    {"id": "PROD-00002", "name": "Cotton T-Shirt", "category": "clothing", "price": 599.00},
    {"id": "PROD-00003", "name": "Desk Lamp", "category": "home", "price": 1299.00},
    {"id": "PROD-00004", "name": "Python Programming Book", "category": "books", "price": 449.00},
    {"id": "PROD-00005", "name": "Yoga Mat", "category": "sports", "price": 899.00},
    {"id": "PROD-00006", "name": "Bluetooth Speaker", "category": "electronics", "price": 3499.00},
    {"id": "PROD-00007", "name": "Running Shoes", "category": "sports", "price": 4999.00},
    {"id": "PROD-00008", "name": "Ceramic Mug Set", "category": "home", "price": 799.00},
    {"id": "PROD-00009", "name": "Data Science Handbook", "category": "books", "price": 699.00},
    {"id": "PROD-00010", "name": "Winter Jacket", "category": "clothing", "price": 3299.00},
]

CITIES = [
    {"city": "Mumbai", "state": "Maharashtra", "pincode": "400001"},
    {"city": "Delhi", "state": "Delhi", "pincode": "110001"},
    {"city": "Bangalore", "state": "Karnataka", "pincode": "560001"},
    {"city": "Chennai", "state": "Tamil Nadu", "pincode": "600001"},
    {"city": "Hyderabad", "state": "Telangana", "pincode": "500001"},
    {"city": "Pune", "state": "Maharashtra", "pincode": "411001"},
    {"city": "Kolkata", "state": "West Bengal", "pincode": "700001"},
]

PAYMENT_METHODS = ["credit_card", "upi", "cod", "debit_card"]
CURRENCIES = ["INR", "USD", "EUR"]
STATUSES = ["placed", "confirmed", "shipped", "delivered"]


def generate_order_event() -> OrderEventV1:
    """Generate a single realistic order event with random but valid data.
    
    Returns:
        OrderEventV1: A fully populated order event with:
            - Random product from PRODUCT_CATALOG
            - Random quantity (1-5 typical, up to 10 for bulk)
            - total_amount = quantity * unit_price
            - Random shipping address from Indian cities
            - Random payment method and currency
    
    CONNECTIONS:
        - Called by: generator.py -> EventGeneratorOrchestrator.generate_batch()
        - Output feeds: Pub/Sub raw-ecommerce-events topic
    """
    raise NotImplementedError("TODO: Implement order event generation using random.choice from constants above")


def generate_order_batch(count: int = 10) -> list[OrderEventV1]:
    """Generate a batch of order events.
    
    Args:
        count: Number of events to generate (default: 10)
    
    Returns:
        list[OrderEventV1]: List of generated order events
    """
    raise NotImplementedError("TODO: Call generate_order_event() in a loop")
