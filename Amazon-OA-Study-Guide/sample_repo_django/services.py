import threading
import uuid
from decimal import Decimal
from typing import Dict, List
from .models import InsufficientInventoryError, Order, OrderItem, ValidationError


class OrderService:
    """Business logic for inventory deduction, pricing, and order creation."""

    def __init__(self, initial_inventory: Dict[str, int]):
        # BUG 2 PREVIOUSLY HERE: Mutable class attribute shared across all instances
        # FIX: Instance-isolated dictionary + threading.Lock to prevent race conditions
        self.inventory: Dict[str, int] = dict(initial_inventory)
        self.orders: Dict[str, Order] = {}
        self._lock = threading.Lock()

    def get_inventory(self, item_id: str) -> int:
        with self._lock:
            return self.inventory.get(item_id, 0)

    def process_order(
        self,
        account_id: str,
        items: List[OrderItem],
        total_amount: Decimal,
        tax_id: str = None,
    ) -> Order:
        """Atomically validates inventory availability and creates an order."""
        with self._lock:
            # 1. Check all items first (All-or-Nothing check)
            for item in items:
                current_stock = self.inventory.get(item.item_id, 0)
                if current_stock < item.quantity:
                    raise InsufficientInventoryError(
                        f"Insufficient inventory for item {item.item_id}: "
                        f"requested {item.quantity}, available {current_stock}"
                    )

            # 2. Deduct inventory atomically
            for item in items:
                self.inventory[item.item_id] -= item.quantity

            # 3. Create order
            order_id = str(uuid.uuid4())
            order = Order(
                order_id=order_id,
                account_id=account_id,
                items=items,
                status="CONFIRMED",
                total_amount=total_amount,
                tax_id=tax_id,
            )
            self.orders[order_id] = order
            return order
