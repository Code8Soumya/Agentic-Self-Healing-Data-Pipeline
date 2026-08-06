"""Generates inventory update events from warehouse systems.

CONNECTIONS:
- Imports: app.models.events.InventoryEvent
- Called by: generator.py (orchestrator)
- Output: Published to Pub/Sub 'raw-ecommerce-events' topic

DATA DOMAIN:
- Warehouses: WH-MUM-01, WH-BLR-02, WH-DEL-03, WH-CHE-04
- Actions: restock, sold, returned, damaged
- Stock ranges: 0-10000 units
"""
import random

from app.models.events import InventoryEvent

WAREHOUSES = ["WH-MUM-01", "WH-BLR-02", "WH-DEL-03", "WH-CHE-04"]
ACTIONS = ["restock", "sold", "returned", "damaged"]
PRODUCT_IDS = [f"PROD-{str(i).zfill(5)}" for i in range(1, 11)]


def generate_inventory_event() -> InventoryEvent:
    """Generate a single inventory update event.

    Returns:
        InventoryEvent: Event with:
            - Random warehouse from WAREHOUSES
            - Random action (restock gives positive qty, sold/damaged gives negative)
            - current_stock is always non-negative

    LOGIC NOTES for implementer:
        - If action == "restock" or "returned": quantity_change should be positive (10-500)
        - If action == "sold" or "damaged": quantity_change should be negative (-1 to -50)
        - current_stock = random base (100-5000) + quantity_change, clamped to >= 0
        - reorder_threshold = random 50-200
    """
    action = random.choice(ACTIONS)
    quantity_change = (
        random.randint(10, 500) if action in ["restock", "returned"]
        else -random.randint(1, 50)
    )
    base_stock = random.randint(100, 5000)
    current_stock = max(0, base_stock + quantity_change)
    return InventoryEvent(
        product_id=random.choice(PRODUCT_IDS),
        warehouse_id=random.choice(WAREHOUSES),
        action=action,
        quantity_change=quantity_change,
        current_stock=current_stock,
        reorder_threshold=random.randint(50, 200)
    )


def generate_inventory_batch(count: int = 10) -> list[InventoryEvent]:
    """Generate a batch of inventory events."""
    return [generate_inventory_event() for _ in range(count)]
