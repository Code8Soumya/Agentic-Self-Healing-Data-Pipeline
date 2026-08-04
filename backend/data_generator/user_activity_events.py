"""Generates user clickstream/activity events.

CONNECTIONS:
- Imports: app.models.events.UserActivityEvent
- Called by: generator.py (orchestrator)
- Output: Published to Pub/Sub 'raw-ecommerce-events' topic

DATA DOMAIN:
- Actions: page_view, add_to_cart, checkout_start, search, wishlist_add
- Device types: mobile, desktop, tablet
- Page URLs: /products/*, /cart, /checkout, /search?q=*, /
"""
import random
import uuid
from datetime import datetime
from app.models.events import UserActivityEvent

ACTIONS = ["page_view", "add_to_cart", "checkout_start", "search", "wishlist_add"]
DEVICE_TYPES = ["mobile", "desktop", "tablet"]
PAGE_URLS = [
    "/", "/products", "/products/PROD-00001", "/products/PROD-00005",
    "/cart", "/checkout", "/search?q=earbuds", "/search?q=shoes",
    "/account/orders", "/wishlist",
]
REFERRERS = [None, "https://google.com", "https://instagram.com", "https://facebook.com", "direct"]


def generate_user_activity_event() -> UserActivityEvent:
    """Generate a single user activity event.
    
    Returns:
        UserActivityEvent: Event with random action, device, page, and referrer.
    
    LOGIC NOTES for implementer:
        - customer_id: random "CUST-" + 5 digit number (range 1-1000)
        - session_id: UUID4 (can reuse same session for multiple events)
        - referrer: 60% chance None, 40% from REFERRERS list
    """
    raise NotImplementedError("TODO: Implement user activity event generation")


def generate_user_activity_batch(count: int = 10) -> list[UserActivityEvent]:
    """Generate a batch of user activity events."""
    raise NotImplementedError("TODO: Call generate_user_activity_event() in a loop")
