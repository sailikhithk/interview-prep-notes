# Amazon OA Question 2: Django, Spring Boot & Node.js Repo Playbook (2026)

> **Platform:** HackerRank Multi-File Project Repository with Embedded AI Coding Assistant  
> **Target Frameworks:** Python (Django / DRF / FastAPI), Java (Spring Boot), TypeScript/JavaScript (Node.js / Express)  
> **Evaluation:** Unit test pass rate, architectural conventions, minimal bug fixes, zero regressions.

---

## 1. The 3 Supported Framework Stacks & File Directory Topologies

When Question 2 starts, HackerRank provisions an isolated micro-environment containing a real web framework codebase. You will typically be given a choice of language (Python, Java, Node.js). 

Here is the exact project topology and where bugs are planted for each framework:

### Stack A: Python (Django & Django REST Framework)
```
project/
├── manage.py
├── settings.py / urls.py
├── api/
│   ├── models.py         <-- Database models, foreign keys, choices
│   ├── serializers.py    <-- Pydantic / DRF serializers, field validation
│   ├── views.py          <-- API endpoints, request parsing, HTTP responses
│   ├── services.py       <-- Business logic (pricing, inventory, discounts)
│   └── urls.py           <-- Route mapping, path parameters
└── tests/
    └── test_views.py     <-- Django TestCase / pytest suite
```
*   **Most Common Planted Bugs in Django:**
    1.  **DRF Serializer Validation:** A field marked as required in `models.py` is omitted in `serializers.py`, or `validate_<field>` raises generic `Exception` instead of `serializers.ValidationError`.
    2.  **Missing `select_related` / `prefetch_related`:** Not causing errors, but causing timeout due to N+1 query limits in automated tests.
    3.  **Django ORM Filter Syntax:** Using `.filter(status="active")` when status is an integer enum, or failing to handle `.first()` returning `None`.
    4.  **Transaction Atomic Boundary:** Missing `@transaction.atomic` causing partial updates when a secondary service raises an error.

---

### Stack B: Java (Spring Boot 3.x / Java 17-21)
```
project/
├── pom.xml / build.gradle
└── src/
    ├── main/java/com/amazon/assessment/
    │   ├── controller/   <-- @RestController, @GetMapping, @PostMapping
    │   ├── service/      <-- @Service business logic, interfaces
    │   ├── repository/   <-- JpaRepository interfaces
    │   ├── model/        <-- @Entity, @Table, DTO records
    │   └── exception/    <-- @ControllerAdvice, custom exceptions
    └── test/java/com/amazon/assessment/
        └── ServiceTest.java <-- JUnit 5 + Mockito tests
```
*   **Most Common Planted Bugs in Spring Boot:**
    1.  **Missing `@RequestBody` or `@Valid`:** In `@PostMapping`, forgetting `@RequestBody` results in `null` DTOs, failing validation tests with HTTP 400 or 500.
    2.  **Unsynchronized Singleton State:** An `@Autowired` `@Service` uses an internal mutable `List` or `Map` instead of `ConcurrentHashMap`, causing race conditions in multi-threaded test cases.
    3.  **Dependency Injection / Bean Wiring:** Forgetting `@Component` / `@Service` on a newly referenced helper class, causing `NoSuchBeanDefinitionException`.
    4.  **JPA Transaction Rollback:** `@Transactional` missing on write methods, or `@Transactional` catching checked exceptions without `rollbackFor = Exception.class`.

---

### Stack C: Node.js (Express / TypeScript)
```
project/
├── package.json / tsconfig.json
├── src/
│   ├── routes/           <-- Express router definitions
│   ├── controllers/      <-- Request/response handlers
│   ├── services/         <-- Business logic classes
│   ├── middleware/       <-- Auth, error handler, validation middleware
│   └── models/           <-- Prisma / Mongoose / In-memory data stores
└── tests/
    └── api.test.ts       <-- Jest / Mocha + Supertest
```
*   **Most Common Planted Bugs in Node.js:**
    1.  **Async/Await Missing:** Forgetting `await` on a promise returned from a service or database call, causing the response to be sent before the data resolves.
    2.  **Express Error Handler Middleware Signature:** Express error handlers MUST take 4 arguments: `(err, req, res, next)`. Forgetting `next` causes Express to treat it as regular middleware, hanging the request timeout.
    3.  **Route Ordering:** Defining `/api/items/:id` BEFORE `/api/items/recent`, causing `:id` to match the string `"recent"`.
    4.  **Mutating Shared Objects:** In-memory array `.push()` instead of immutably spreading `[...items]`, leading to test pollution between consecutive Jest runs.

---

## 2. Framework-Specific AI Prompting Cheat Sheet

When you prompt the embedded AI assistant in Question 2, cite the exact framework paradigms so it gives pinpoint code fixes:

### For Django Repos:
> **Prompt:** *"Unit test `test_create_order_invalid_coupon` is expecting HTTP 400 with `{'error': 'Invalid coupon'}`, but receives HTTP 500. Inspect `OrderSerializer.validate` in `api/serializers.py` and explain why `serializers.ValidationError` is not being caught properly."*

### For Spring Boot Repos:
> **Prompt:** *"JUnit test `testConcurrentCheckout` in `OrderServiceTest.java` is failing with assertion mismatch on stock quantity. In `OrderServiceImpl.java`, how is inventory decremented? Show the fix to use `AtomicInteger` or synchronized block."*

### For Node.js / Express Repos:
> **Prompt:** *"Jest test `GET /orders/:id` times out after 5000ms in `tests/api.test.ts`. Inspect `src/controllers/orderController.ts` on line 34. Is there a missing `await` or is `res.status().json()` not being called on the error branch?"*

---

## 3. The 3 Golden Rules of HackerRank Repo Challenges

1. **Rule of Minimum Intervention:**  
   Never refactor code that is already passing tests. Fix ONLY the lines that trigger red test failures.
2. **Never Touch the Test Assertions:**  
   In some repos, test files are editable. If you change test assertions to make them pass, automated grading scripts will flag this as test tampering and give 0 points.
3. **Beware In-Memory State Leakage:**  
   If tests pass individually but fail when run together, check for global arrays/maps that need to be reset in `setUp()` or `beforeEach()`.
