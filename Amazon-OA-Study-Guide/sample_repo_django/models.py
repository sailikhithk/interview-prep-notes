import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional


class ValidationError(Exception):
    """Custom exception raised when payload validation fails."""

    pass


class InsufficientInventoryError(Exception):
    """Raised when inventory is less than order request."""

    pass


@dataclass
class OrderItem:
    item_id: str
    quantity: int
    unit_price: Decimal


@dataclass
class Order:
    order_id: str
    account_id: str
    items: List[OrderItem]
    status: str
    total_amount: Decimal
    tax_id: Optional[str] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
