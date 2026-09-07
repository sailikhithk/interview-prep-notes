import concurrent.futures
from decimal import Decimal
import pytest
from .models import InsufficientInventoryError, ValidationError
from .serializers import OrderSerializer
from .services import OrderService


def test_order_serializer_valid_payload():
    payload = {
        "account_id": "acc-12345",
        "items": [
            {"item_id": "item-A", "quantity": 2, "unit_price": "19.99"},
            {"item_id": "item-B", "quantity": 1, "unit_price": "49.50"},
        ],
        "tax_id": "US-TX-9988",
    }
    validated = OrderSerializer.validate(payload)
    assert validated["account_id"] == "acc-12345"
    assert len(validated["items"]) == 2
    assert validated["total_amount"] == Decimal("89.48")
    assert validated["tax_id"] == "US-TX-9988"


def test_order_serializer_optional_tax_id():
    """Verify bugfix: missing tax_id should NOT raise ValidationError."""
    payload = {
        "account_id": "acc-12345",
        "items": [{"item_id": "item-A", "quantity": 1, "unit_price": "10.00"}],
    }
    validated = OrderSerializer.validate(payload)
    assert validated["tax_id"] is None
    assert validated["total_amount"] == Decimal("10.00")


def test_order_service_insufficient_inventory():
    service = OrderService(initial_inventory={"item-A": 5})
    payload = {
        "account_id": "acc-123",
        "items": [{"item_id": "item-A", "quantity": 10, "unit_price": "5.00"}],
    }
    validated = OrderSerializer.validate(payload)

    with pytest.raises(InsufficientInventoryError):
        service.process_order(
            account_id=validated["account_id"],
            items=validated["items"],
            total_amount=validated["total_amount"],
        )

    # Stock should remain unchanged
    assert service.get_inventory("item-A") == 5


def test_order_service_concurrent_deduction():
    """Verify bugfix: thread safety under 20 concurrent orders competing for 10 units."""
    service = OrderService(initial_inventory={"item-HOT": 10})

    successful_orders = 0
    failed_orders = 0

    def place_order(i):
        payload = {
            "account_id": f"acc-{i}",
            "items": [
                {"item_id": "item-HOT", "quantity": 1, "unit_price": "15.00"}
            ],
        }
        val = OrderSerializer.validate(payload)
        try:
            service.process_order(
                val["account_id"], val["items"], val["total_amount"]
            )
            return True
        except InsufficientInventoryError:
            return False

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(place_order, i) for i in range(25)]
        for fut in concurrent.futures.as_completed(futures):
            if fut.result():
                successful_orders += 1
            else:
                failed_orders += 1

    assert successful_orders == 10
    assert failed_orders == 15
    assert service.get_inventory("item-HOT") == 0
