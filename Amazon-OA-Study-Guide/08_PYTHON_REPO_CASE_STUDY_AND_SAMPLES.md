# Case Study: Real-World Amazon Multi-File Python Repository Debugging (2026)

> **Role Focus:** AWS / Amazon Software Development Engineer (SDE)  
> **Question Type:** Question 2 — Code Repository Environment (Python / Django Stack)  
> **Simulated Codebase:** Located in [`sample_repo_django/`](sample_repo_django/)  
> **Running the Suite:** `python3 -m pytest sample_repo_django/test_order_system.py`

---

## 1. Problem Statement & Architecture Context

You are given an e-commerce order management service designed in Python mimicking Django REST Framework / Pydantic patterns.

The codebase consists of:
- `models.py`: Defines dataclasses for `OrderItem`, `Order`, and custom exceptions (`ValidationError`, `InsufficientInventoryError`).
- `serializers.py`: Validates incoming HTTP payloads, ensures mandatory fields exist, calculates line totals, and parses tax IDs.
- `services.py`: Manages inventory levels in an atomic order processing workflow.
- `test_order_system.py`: Automated unit and concurrent load tests.

When you launch the environment and run `pytest`, **2 out of 4 tests FAIL**:
1. `test_order_serializer_optional_tax_id`: Fails with `ValidationError: tax_id is required`.
2. `test_order_service_concurrent_deduction`: Fails because multiple concurrent threads cause overselling (stock ends up negative or successful orders exceed available inventory).

---

## 2. Bug 1: Serializer Over-Strict Validation

### Symptom & Stack Trace:
```text
FAILED sample_repo_django/test_order_system.py::test_order_serializer_optional_tax_id
E   ValidationError: tax_id is required
sample_repo_django/serializers.py:42: ValidationError
```

### The Broken Code in `serializers.py`:
```python
# BROKEN VERSION
tax_id = data.get("tax_id")
if not tax_id:
    raise ValidationError("tax_id is required")  # <-- BUG: tax_id is optional!
```

### Forensic AI Assistant Prompt:
> *"Unit test `test_order_serializer_optional_tax_id` in `test_order_system.py` failed with `ValidationError: tax_id is required`. In `models.py`, `tax_id` is defined as `Optional[str] = None`. How should `OrderSerializer.validate` handle missing or None `tax_id`?"*

### AI Diagnosis & The Fix:
`tax_id` should be optional. Only validate its type if it is provided:
```python
# FIXED VERSION
tax_id = data.get("tax_id")
if tax_id is not None and not isinstance(tax_id, str):
    raise ValidationError("tax_id must be a string if provided")
```

---

## 3. Bug 2: Race Condition & Concurrency Overselling

### Symptom & Stack Trace:
```text
FAILED sample_repo_django/test_order_system.py::test_order_service_concurrent_deduction
E   AssertionError: assert 14 == 10
E     where 14 = successful_orders
E     and 10 = initial inventory
```

### The Broken Code in `services.py`:
```python
# BROKEN VERSION
class OrderService:
    inventory = {}  # BUG 2A: Shared class-level attribute across tests!

    def __init__(self, initial_inventory):
        self.inventory = initial_inventory

    def process_order(self, account_id, items, total_amount, tax_id=None):
        # BUG 2B: Check-then-act race condition without locking
        for item in items:
            if self.inventory.get(item.item_id, 0) < item.quantity:
                raise InsufficientInventoryError(...)

        # Context switch happens here! Multiple threads pass the check!
        for item in items:
            self.inventory[item.item_id] -= item.quantity
```

### Forensic AI Assistant Prompt:
> *"Test `test_order_service_concurrent_deduction` runs 25 concurrent threads competing for 10 units of inventory. 14 orders succeeded instead of 10. Explain why `process_order` in `services.py` suffers from a race condition and show how to make inventory deduction thread-safe using `threading.Lock`."*

### AI Diagnosis & The Fix:
Add `threading.Lock` to guarantee atomic check-and-decrement:
```python
# FIXED VERSION
import threading


class OrderService:

    def __init__(self, initial_inventory: Dict[str, int]):
        self.inventory: Dict[str, int] = dict(initial_inventory)
        self.orders: Dict[str, Order] = {}
        self._lock = threading.Lock()

    def process_order(
        self,
        account_id: str,
        items: List[OrderItem],
        total_amount: Decimal,
        tax_id: str = None,
    ) -> Order:
        with self._lock:  # ATOMIC EXECUTION BOUNDARY
            for item in items:
                current_stock = self.inventory.get(item.item_id, 0)
                if current_stock < item.quantity:
                    raise InsufficientInventoryError(...)

            for item in items:
                self.inventory[item.item_id] -= item.quantity

            order = Order(...)
            self.orders[order.order_id] = order
            return order
```

---

## 4. Verification Pass

Execute the test suite in your terminal:
```bash
python3 -m pytest sample_repo_django/test_order_system.py -v
```

Expected Output:
```text
============================= test session starts ==============================
collected 4 items

sample_repo_django/test_order_system.py::test_order_serializer_valid_payload PASSED   [ 25%]
sample_repo_django/test_order_system.py::test_order_serializer_optional_tax_id PASSED [ 50%]
sample_repo_django/test_order_system.py::test_order_service_insufficient_inventory PASSED [ 75%]
sample_repo_django/test_order_system.py::test_order_service_concurrent_deduction PASSED [100%]

============================== 4 passed in 0.06s ===============================
```
All tests green, zero regressions, thread-safe inventory controls guaranteed.
