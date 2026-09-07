from decimal import Decimal
from typing import Any, Dict
from .models import OrderItem, ValidationError


class OrderSerializer:
    """Validates incoming HTTP order payload mimicking DRF / Pydantic."""

    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, Any]:
        account_id = data.get("account_id")
        if not account_id or not isinstance(account_id, str):
            raise ValidationError("account_id is required and must be a string")

        items_data = data.get("items")
        if not items_data or not isinstance(items_data, list):
            raise ValidationError("items must be a non-empty list")

        validated_items = []
        total = Decimal("0.00")
        for item in items_data:
            item_id = item.get("item_id")
            qty = item.get("quantity")
            price_val = item.get("unit_price")

            if not item_id:
                raise ValidationError("item_id is required in each item")
            if not isinstance(qty, int) or qty <= 0:
                raise ValidationError("quantity must be a positive integer")
            if price_val is None:
                raise ValidationError("unit_price is required")

            unit_price = Decimal(str(price_val))
            if unit_price <= 0:
                raise ValidationError("unit_price must be positive")

            validated_items.append(
                OrderItem(item_id=item_id, quantity=qty, unit_price=unit_price)
            )
            total += unit_price * qty

        # BUG 1 PREVIOUSLY HERE: Required tax_id strictly, causing failures when optional
        # FIX: tax_id is optional; default to None if omitted or empty
        tax_id = data.get("tax_id")
        if tax_id is not None and not isinstance(tax_id, str):
            raise ValidationError("tax_id must be a string if provided")

        return {
            "account_id": account_id,
            "items": validated_items,
            "total_amount": total,
            "tax_id": tax_id,
        }
