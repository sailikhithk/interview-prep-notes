# Java & Spring Boot Interview Prep Notes

This section covers core Java 21 and Spring Boot 3.x concepts referenced in the Dose Management System (DMS) onboarding and developer interview guide.

---

## 1. Dependency Injection: Constructor vs Field Autowired

### Problem Statement
Why prefer constructor injection (typically via Lombok `@RequiredArgsConstructor`) over field `@Autowired`?

```java
// Avoid:
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;
}

// Prefer:
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
}
```

### Analysis & Interview Responses

| Aspect | Field Injection (`@Autowired`) | Constructor Injection (`@RequiredArgsConstructor`) |
|---|---|---|
| **Immutability** | Fields cannot be `final`. They can be re-assigned or mutate at runtime. | Fields are `final`. Once initialized, they are immutable. |
| **Null Safety / Fail-Fast** | Class can be instantiated with `new` in unit tests, resulting in `NullPointerException` at runtime if fields aren't set. | Compiler forces dependencies to be passed. Null-safety is guaranteed at compilation. |
| **Dependency Visibility** | Hidden. You must inspect the private fields to see what the class depends on. | Explicit. The constructor signature clearly documents all dependencies. |
| **Testing** | Requires reflection (e.g. `ReflectionTestUtils`) or Spring context boot to inject mocks. | Simple unit testing. Pass mock instances directly into the constructor: `new UserService(mockRepo)`. |

---

## 2. JPA/Hibernate Entity State & Lazy vs Eager Fetching

### Problem Statement
Explain `FetchType.LAZY` vs `FetchType.EAGER` and how to avoid the N+1 Select Problem.

### Core Concepts

*   **`FetchType.LAZY`**: Hibernate fetches the association on first access.
    *   *Implementation*: A proxy subclass or dynamic proxy is created. The relationship field contains a `PersistentBag` or proxy object that queries the database only when getter/methods are called.
    *   *Risk*: If accessed outside an active Hibernate session boundary, throws `LazyInitializationException`.
*   **`FetchType.EAGER`**: Hibernate fetches the association immediately with the parent entity.
    *   *Risk*: Causes huge overhead if multiple relationships are EAGER, performing multiple cartesian product JOINs or separate queries.

### The N+1 Select Problem
If you have a `Parent` entity with a LAZY `List<Child>` collection, querying all parents:
```java
List<Parent> parents = repository.findAll(); // 1 query
for (Parent p : parents) {
    p.getChildren().size(); // N queries (one for each parent)
}
```
Total queries: **N + 1**.

#### Mitigations

1.  **`@EntityGraph`**:
    Specifies fetch graph dynamically for a query.
    ```java
    @Repository
    public interface ParentRepository extends JpaRepository<Parent, Long> {
        @EntityGraph(attributePaths = {"children"})
        List<Parent> findAll();
    }
    ```
2.  **JOIN FETCH**:
    Write custom JPQL or Criteria queries to fetch associations eagerly in a single database query.
    ```sql
    SELECT p FROM Parent p JOIN FETCH p.children
    ```

---

## 3. Spring Transaction Management (`@Transactional`)

### Problem Statement
How does `@Transactional` work, and why does placing it on a `private` method fail?

### Spring AOP & Proxies
Spring implements `@Transactional` using **Aspect-Oriented Programming (AOP)** and **Dynamic Proxies** (CGLIB or JDK dynamic proxies).

```
[Client] ---> [Spring Proxy (Wraps Service Bean)] ---> [Target Service Bean]
                  |                                           |
                  |-- 1. Start Transaction                    |
                  |-- 2. Call target method ------------->    |
                  |                                 (Executes business logic)
                  |-- 3. Commit/Rollback <-----------------|
```

#### Why `private` methods fail
If a method is annotated with `@Transactional` but is `private` (or package-private/protected in CGLIB's default configuration), Spring's proxy wrapper cannot intercept the call. CGLIB creates a subclass of the bean and overrides the `public` methods to insert transaction logic. It cannot override `private` methods.

#### Self-Invocation Pitfall
If method `A` calls method `B` inside the same bean class:
```java
@Service
public class OrderService {
    public void createOrder() {
        // self-invocation: bypasses proxy
        saveOrderInternal(); 
    }

    @Transactional
    public void saveOrderInternal() {
        // Transaction will NOT start here!
    }
}
```
*Correction*: The call to `saveOrderInternal()` bypasses the Spring proxy and directly calls the target object, so the transactional logic is never executed.

---

## 4. Concurrent Updates: Optimistic vs Pessimistic Locking

### Optimistic Locking
*   **Mechanism**: Uses a `@Version` field (integer or timestamp) on the JPA entity.
    ```java
    @Version
    private Long version;
    ```
*   **Behavior**: When Hibernate executes an UPDATE, it adds the version to the `WHERE` clause:
    ```sql
    UPDATE order SET name = ?, version = version + 1 WHERE id = ? AND version = ?
    ```
    If no rows are updated (version changed in DB since read), Hibernate throws an `OptimisticLockException`.
*   **Best Used**: Read-heavy systems with low probability of write conflicts.

### Pessimistic Locking
*   **Mechanism**: Locks the database row directly using database-level locking mechanisms.
    ```java
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT o FROM Order o WHERE o.id = :id")
    Order findByIdForUpdate(Long id);
    ```
*   **Behavior**: Issues a `SELECT ... FOR UPDATE` statement, blocking other transactions from writing to or locking the row until the transaction commits.
*   **Best Used**: High-concurrency, write-heavy systems where conflicts are frequent and must be blocked immediately.
