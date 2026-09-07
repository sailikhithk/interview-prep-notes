# Amazon OA: Code Repository & AI Coding Assistant Playbook (2026)

> **Section:** Coding Challenge — Problem 2 (Code Repository Environment)  
> **Target Time:** 50–55 minutes  
> **Core Objective:** Debug, refactor, and pass 100% of unit tests in an unfamiliar multi-file production codebase using an integrated AI coding assistant.

---

## 1. What is the Code Repository Environment?

Unlike Question 1 (a single function template), Question 2 opens a **complete software project structure** inside HackerRank.
You will see:
- A directory tree with multiple packages/modules (e.g., controllers, services, repositories, schemas, models).
- Build and configuration files (`package.json`, `pom.xml`, `requirements.txt`, `Makefile`).
- A full suite of automated unit/integration tests (`tests/`).
- An embedded **AI Coding Assistant panel** on the side of the IDE.

### Typical Real-World Problem Types:
1. **Broken REST API Endpoint:** A route returns HTTP 500 or incorrect JSON structure due to missing validation or incorrect DTO mapping.
2. **Race Condition / Concurrency Bug:** In-memory inventory or rate-limiter loses counts under multi-threaded requests.
3. **Data Serialization / Type Mismatch:** Pydantic / Jackson / TypeScript schema validation fails due to datetime formatting or null handling.
4. **Failing Business Rules in Service Layer:** Discount logic, tax calculations, or auth permission checks return wrong outcomes for edge cases.

---

## 2. The 5-Phase Diagnostic Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       5-PHASE REPO EXECUTION PROTOCOL                        │
├───────────────┬───────────────┬───────────────┬───────────────┬─────────────┤
│ 1. EXPLORE    │ 2. REPRODUCE  │ 3. TARGETED AI│ 4. SURGICAL   │ 5. VERIFY & │
│ (Minutes 0-5) │ (Minutes 5-10)│ (Minutes 10-25│ (Minutes 25-45│ (Mins 45-55)│
├───────────────┼───────────────┼───────────────┼───────────────┼─────────────┤
│ • Read README │ • Run test    │ • Ask AI to   │ • Apply line- │ • Re-run    │
│ • Inspect     │   suite       │   trace exact │   level patch │   full suite│
│   file tree   │ • Note failed │   failures    │ • Avoid broad │ • Check for │
│ • Check build │   assertions  │ • Formulate   │   rewrites    │   regression│
│   command     │   & errors    │   hypothesis  │ • Add checks  │ • Submit    │
└───────────────┴───────────────┴───────────────┴───────────────┴─────────────┘
```

### Phase 1: Explore (5 mins)
- Open `README.md` or problem description to understand the business intent.
- Inspect the file tree. Identify the core entry points:
  - Where is the service logic? (e.g., `src/services/` or `com/amazon/service/`)
  - Where are the tests? (e.g., `tests/` or `src/test/`)
- **Important Language Lock:** Ensure you confirm your preferred language (Python or Java) before typing anything. You cannot change it once selected!

### Phase 2: Reproduce & Capture Failures (5 mins)
- Click **Run Tests** (or execute the test command in the terminal).
- Read the test output carefully:
  - How many tests passed? (e.g., `12 passed, 3 failed`).
  - Read the exact assertion errors (e.g., `AssertionError: Expected status 200, got 403` or `KeyError: 'discount_code'`).
  - Note the filenames and line numbers cited in the stack traces.

### Phase 3: Targeted AI Prompting (15 mins)
**Never type:** *"Fix this codebase for me"* or *"Make all tests pass."* The AI will generate hallucinated pseudo-code or delete tests to make them "pass."

**Always use Targeted Forensic Prompts:**
- **Prompt 1 (Codebase Navigation):**  
  > *"Where in the repository is the logic that calculates shipping fees for prime members? List the file and function name."*
- **Prompt 2 (Stack Trace Diagnosis):**  
  > *"Test `test_apply_coupon_expired` failed with `AssertionError: False != True` at `tests/test_coupon.py:42`. What conditions in `CouponService.validate_coupon` can cause an expired coupon to return True?"*
- **Prompt 3 (Hypothesis Testing):**  
  > *"Here is the method `process_order` from `order_service.py`. If `inventory_count < requested_quantity`, does it raise `InsufficientInventoryException` or return None? Explain the error handling path."*

### Phase 4: Surgical Implementation (20 mins)
- Navigate directly to the affected source file.
- Implement the minimal, clean fix that satisfies the contract.
- Maintain existing codebase conventions:
  - If the codebase uses typing (`typing.Optional`, `typing.List`), use typing.
  - If it uses custom exceptions (e.g., `ValidationError`), import and raise that specific exception, not generic `Exception`.
  - Preserve existing comments and docstrings.

### Phase 5: Verification & Regression Shield (10 mins)
- Run the test suite again.
- Verify:
  - Did the previously failing tests turn green?
  - Did any previously passing tests turn red? (Zero regressions allowed).
- Write or uncomment any edge case tests if prompted in the instructions.
- Ensure the project builds cleanly without linting/syntax warnings.
- Click **Submit**.

---

## 3. Top Architectural Pitfalls in Repo Challenges

### Pitfall 1: Mutating Shared In-Memory State (Concurrency Bugs)
- **Symptom:** Tests pass when run in isolation, but fail intermittently or fail during parallel test execution.
- **Cause:** Class attributes or global dictionaries shared across test instances:
  ```python
  # BUGGY: Class-level mutable dictionary
  class CartService:
      cart_items = {}  # Shared across all requests!
```
- **Fix:** Initialize state inside `__init__`:
  ```python
  class CartService:

      def __init__(self):
          self.cart_items = {}  # Instance-isolated
```

### Pitfall 2: Off-By-One & Timezone Handling
- **Symptom:** `test_token_expiry` fails by 1 second or fails due to UTC vs. local time.
- **Cause:** Using `datetime.now()` instead of `datetime.now(timezone.utc)` or `<` instead of `<=`.
- **Fix:** Always ensure naive vs. timezone-aware datetimes match across models and validators.

### Pitfall 3: Null / Optional Attribute Dereferencing
- **Symptom:** `TypeError: 'NoneType' object is not subscriptable` or `AttributeError`.
- **Cause:** Assuming nested JSON fields always exist.
- **Fix:** Safe dictionary access (`payload.get("metadata", {}).get("tag")`) or optional chaining.

---

## 4. AI Assistant Rules of Engagement

| Do's | Don'ts |
| :--- | :--- |
| Ask the AI to locate relevant files and symbols across modules. | Never ask the AI to re-architect entire modules from scratch. |
| Paste specific error stack traces to get an explanation of the failure mode. | Never copy-paste AI code without reading every single line. |
| Ask the AI to write a targeted unit test verifying an edge case. | Never let the AI modify configuration or test assertion thresholds. |
| Verify AI suggestions against the problem statement constraints. | Never assume the AI has access to hidden HackerRank test cases. |
