# DMS Developer Interview Guide

> **Role**: Full-Stack Developer (Java + React)
> **Project**: Dose Management System — Eli Lilly
> **Tech Stack**: Java 21 / Spring Boot 3.x / Spring 6 / PostgreSQL / JPA-Hibernate / Flyway / React 18 / TypeScript / MUI / Jotai / AWS (SES, S3, SNS) / Docker / GitOps
> **Last Updated**: 2026-05-15
> **Checklist Sync**: Aligned with `docs/themes/code-quality/workflows/*_code_review_checklist.md` + `skills/code-review-checklist.md` (9-Layer)

---

## Table of Contents

1. [Interview Structure](#interview-structure)
2. [Phase 1: Intro & Experience](#phase-1-intro--experience-10-min)
3. [Phase 2: Backend — Java / Spring Boot](#phase-2-backend--java--spring-boot-25-min)
4. [Phase 3: Database & Migrations](#phase-3-database--migrations-15-min)
5. [Phase 4: Frontend — React / TypeScript](#phase-4-frontend--react--typescript-20-min)
6. [Phase 5: DevOps & Process](#phase-5-devops--process-10-min)
7. [Phase 6: Domain & Architecture](#phase-6-domain--architecture-10-min)
8. [Advanced Grilling — Spring Boot Deep Dive](#advanced-grilling--spring-boot-deep-dive)
9. [Advanced Grilling — Lazy Loading Deep Dive](#advanced-grilling--lazy-loading-deep-dive)
10. [Advanced Grilling — Kafka / Event-Driven](#advanced-grilling--kafka--event-driven)
11. [Advanced Grilling — Database Blind Spots](#advanced-grilling--database-blind-spots)
12. [Advanced Grilling — React Depth Check](#advanced-grilling--react-depth-check)
13. [Advanced Grilling — System Design / DMS Scenarios](#advanced-grilling--system-design--dms-scenarios)
14. [Advanced Grilling — DMS Production Anti-Patterns](#advanced-grilling--dms-production-anti-patterns-checklist-sync)
15. [Resume Weak-Area Probes](#resume-weak-area-probes)
16. [Scoring Rubric](#scoring-rubric)
17. [Candidate Questions to Prepare For](#candidate-questions-to-prepare-for)
18. [30/60/90 Day Onboarding](#306090-day-onboarding-suggestion)
19. [Appendix: Checklist ↔ Interview Cross-Reference](#appendix-checklist--interview-cross-reference)

---

## Interview Structure

**Standard interview (90 min):** Use Phases 1–6 (24 questions).
**Deep technical grilling (120 min):** Add Advanced Grilling sections selectively based on resume gaps.
**Resume gap probing:** Use the Resume Weak-Area Probes section to target specific gaps per candidate.

| Phase | Duration | Focus |
|-------|----------|-------|
| 1. Intro & Experience | 10 min | Background, motivation |
| 2. Backend (Java/Spring) | 25 min | Core skills for our stack |
| 3. Database & Migrations | 15 min | Schema design, Flyway, audit trails |
| 4. Frontend (React/TS) | 20 min | Component patterns, state management |
| 5. DevOps & Process | 10 min | CI/CD, Git workflow, deployment |
| 6. Domain & Architecture | 10 min | Layered architecture, security mindset |
| **Advanced Grilling** | +30 min | Pick sections based on candidate's claimed strengths/gaps |

---

## Phase 1: Intro & Experience (10 min)

- Walk me through your most recent project. What was your role?
- Have you worked in a regulated industry (pharma, healthcare, finance)?
- What's the largest codebase you've contributed to? How many services/tables?
- How do you approach joining a project mid-sprint with an existing codebase?

---

## Phase 2: Backend — Java / Spring Boot (25 min)

### Fundamentals (warm-up)

**Q1: Dependency Injection** — We use constructor injection exclusively (`@RequiredArgsConstructor`). Why would we prefer that over field `@Autowired`?

> **Expected**: Testability (can pass mocks via constructor), immutability (fields are `final`), fail-fast on missing beans (app won't start), explicit dependencies (constructor signature shows what's needed).
>
> **Red flag**: Says "field injection is fine" or "I use `@Autowired` on fields."

**Q2: Layered Architecture** — In a Controller → Service → Repository pattern, what should each layer return? Should a controller ever contain business logic?

> **Expected**: Controllers return `ResponseEntity` wrapping DTOs. Services return DTOs (never entities). Repositories return entities. No business logic in controllers — controllers only delegate to services.
>
> **Red flag**: Returns entities from the service layer or puts validation logic in controllers.

### Intermediate

**Q3: JPA/Hibernate** — What's the difference between `FetchType.LAZY` and `EAGER`? When would you use `@EntityGraph`?

> **Expected**: LAZY loads on first access (proxy/PersistentCollection), EAGER loads immediately with parent query. Default to LAZY always. Use `@EntityGraph` when a specific query needs to load a relationship in one query (avoids N+1) without changing the entity's default fetch strategy.
>
> **Red flag**: Says "use EAGER to avoid LazyInitializationException."

**Q4: Transactions** — A method calls `repository.save(parent)` then `repository.save(child)`. The child save fails. What happens to the parent save without `@Transactional`?

> **Expected**: Without `@Transactional`, each `save()` is its own transaction. Parent persists, child doesn't. Data inconsistency — orphaned parent. With `@Transactional`, both are in one transaction and the parent save rolls back too.
>
> **Follow-up**: "What if `@Transactional` is on a `private` method?" → It doesn't work. Spring's proxy-based AOP only intercepts public methods called from outside the class.

**Q5: Audit Trail Pattern (Real DMS Bug)** — Every UPDATE in our system must set `changed_by` and `changed_on`. A developer writes:

```java
entity.setName(dto.getName());
entity.setChangedBy(currentUser);
if (isDataChanged(dto, entity)) {
    repository.save(entity);
}
```

What's the bug?

> **Expected**: `isDataChanged()` is called AFTER the setters — the entity already matches the DTO at that point, so it always returns false. The `save()` never executes. Must compare BEFORE modifying the entity. This is a real bug pattern we've fixed (CMCDOS-2966).
>
> **This is a critical question.** If the candidate spots it immediately, they understand the compare-before-mutate pattern.

### Advanced

**Q6: Concurrency** — Two users submit conflicting updates to the same dose order. How would you prevent lost updates?

> **Expected**: Optimistic locking (`@Version` field on entity). Hibernate automatically checks the version on UPDATE and throws `OptimisticLockException` if it's stale. Handle via `@ControllerAdvice` → return 409 Conflict with "record was modified by another user."
>
> **Bonus**: Mentions pessimistic locking (`@Lock(LockModeType.PESSIMISTIC_WRITE)`) for critical sections, or compare-and-set patterns.

**Q7: Exception Handling** — How do you structure error responses in a REST API? What should NOT appear in a production error response?

> **Expected**: Consistent error contract: `{ "error": "<Category>", "message": "<Human-readable>", "timestamp": "<ISO 8601>", "status": <HTTP code> }`. Never expose stack traces, `e.getMessage()`, SQL errors, or internal class names. Use `@ControllerAdvice` with domain-specific exceptions.
>
> **Red flag**: `throw new RuntimeException(e.getMessage())` in a controller.

---

## Phase 3: Database & Migrations (15 min)

### Schema Design

**Q8: Audit Columns** — Every table has `created_on`, `created_by`, `changed_on`, `changed_by`. On an INSERT, what should `changed_on`/`changed_by` be?

> **Expected**: NULL. They should only be populated on UPDATE. Setting them on INSERT is a bug — you can't distinguish "never modified" from "modified at creation time." It corrupts the audit trail.
>
> **This is a real DMS bug we've fixed.**

**Q9: Soft Delete** — Why would a pharmaceutical system use soft deletes (status column) instead of hard deletes for dose orders?

> **Expected**: Regulatory audit trail (FDA/GxP compliance), data recovery, historical reporting, compliance requirements. Every state change must be traceable. Even "cancelled" orders may need investigation.
>
> **Green flag**: Mentions regulatory requirements without being prompted.

### Flyway Migrations

**Q10: Idempotency** — Why must every Flyway migration be idempotent? What happens if a migration partially fails?

> **Expected**: Flyway marks the failed migration in `flyway_schema_history`. ALL subsequent migrations are blocked until the failed one is manually repaired. This is why migrations must use `IF NOT EXISTS`, `DO $$ ... END $$` guards — so re-running after a partial failure doesn't crash.
>
> **Red flag**: "Just delete the row from flyway_schema_history."

**Q11: Production Schema Change** — You need to add a NOT NULL column to a table with 500K rows in production. How do you handle it?

> **Expected**: Multi-step migration:
> 1. `ALTER TABLE ADD COLUMN approval_status VARCHAR(50)` — nullable, no lock
> 2. `UPDATE table SET approval_status = 'PENDING' WHERE approval_status IS NULL` — backfill in batches
> 3. `ALTER TABLE ALTER COLUMN approval_status SET NOT NULL` — brief lock, data already backfilled
>
> **Red flag**: Single `ADD COLUMN ... NOT NULL DEFAULT 'PENDING'` statement on a 500K row table — locks the entire table.

### Data Integrity

**Q12: Parent-Child Reconciliation** — A protocol has child collections (sites, approvers, products, patients). On update, the frontend sends the full list. How do you reconcile without losing data?

> **Expected**: In-place reconciliation — match existing children by ID, update in-place, insert truly new ones (no ID), delete those not in the DTO (orphanRemoval). NOT `clear()+addAll()` which causes Hibernate to DELETE all rows then INSERT them as new — IDs change, audit trail breaks.
>
> **This is CMCDOS-3150.** If they get this, they deeply understand JPA collection management.

---

## Phase 4: Frontend — React / TypeScript (20 min)

### Fundamentals

**Q13: Functional Components** — We use functional components only. Why no class components in a modern React codebase?

> **Expected**: Hooks composability (custom hooks extract reusable logic), simpler testing (no `this` binding), better tree-shaking, smaller bundle size, React team direction (all new features are hooks-based), and class components can't use `useContext`/`useMemo`/`useCallback` etc.

**Q14: State Management** — We use Context API + Jotai atoms + localStorage. When would you choose each?

> **Expected**: Context for auth/theme (infrequent changes, many consumers). Jotai for fine-grained reactive state (frequent changes without re-rendering entire tree — atom-level granularity). localStorage for persistence across sessions/tabs (tokens, preferences).
>
> **Key insight**: Context re-renders ALL consumers on ANY change. Jotai only re-renders components that read the specific atom that changed.

### Practical

**Q15: TypeScript** — Given this type, what's the problem?

```typescript
interface DoseOrder {
  doseOrderNumber: number;
  status: string;
  createdOn: string;
}
```

> **Expected**: (1) `status` should be a union type `'PENDING' | 'APPROVED' | 'REJECTED' | 'CANCELLED'` — `string` loses type safety. (2) `createdOn` as raw string needs date parsing everywhere it's used — should use a centralized `dateUtils` for formatting. (3) Status values should come from an enum in `constants/enums.ts`, not be hardcoded.

**Q16: MUI Styling** — A developer adds `style={{ color: 'red', fontSize: '14px' }}` to a component. What's wrong with this approach?

> **Expected**: Use `sx` prop or `styled()`. Inline styles bypass the theme (can't use theme breakpoints, colors, spacing). Hardcoded hex values violate the design system. Use theme color tokens: `sx={{ color: 'error.main', fontSize: theme.typography.body2.fontSize }}`.
>
> **Red flag**: "Inline styles are fine for one-off things."

### Security

**Q17: Route Guards** — Our frontend has role-based route guards. Is that sufficient for security?

> **Expected**: NO. Frontend guards are UX only. Backend MUST independently verify permissions. An attacker can bypass route guards by typing the URL directly, modifying localStorage, or using browser DevTools. This is a real vulnerability we've patched (CMCDOS-2302, CMCDOS-2329).
>
> **Must-pass question.** If they say "yes, route guards are enough" — red flag.

### Advanced

**Q18: Performance** — A data grid renders 500 dose orders and re-renders on every keystroke in a search field. How do you fix it?

> **Expected**: (1) Debounce the search input (300ms). (2) `useMemo` the filtered rows so reference is stable when data hasn't changed. (3) `React.memo` on the grid component. (4) Virtualization for large lists (only render visible rows). (5) Separate search state from grid data state.
>
> **Red flag**: "Just use `useCallback`" — that's for functions, not data.

---

## Phase 5: DevOps & Process (10 min)

**Q19: Git Workflow** — We use feature branches off sprint branches (not main). PRs target the sprint branch. Why?

> **Expected**: Isolate sprint work, allow parallel sprint development (R1.2 and R2.0 simultaneously), controlled merges to main at release boundaries, rollback isolation (can drop an entire sprint branch if needed).

**Q20: CI/CD** — Our pipeline runs 5 checks before merge. A developer pushes and CI fails on "Migration Check — version conflict." What happened and how do you fix it?

> **Expected**: Two developers created migrations with the same version number on separate branches. Fix: re-number your migration to the next available version. Prevention: always `git fetch origin && git merge` base branch before creating a migration.

**Q21: Docker** — What's the difference between a multi-stage Docker build and a single-stage? Why do we use multi-stage?

> **Expected**: Multi-stage: first stage compiles/builds, second stage copies only the artifact. Result: smaller final image (no JDK/npm/build tools), security (no source code in production image), faster deploys (smaller image push/pull).

---

## Phase 6: Domain & Architecture (10 min)

**Q22: Security Mindset** — An external user (site requester) calls an API endpoint that should only be accessible to internal users. The frontend hides the button. Is this a bug?

> **Expected**: YES — backend must enforce access control independently. Frontend hiding is UX, not security. Need `@PreAuthorize` or service-layer checks using `SecurityUtils.getCurrentUserId()`. Never trust the client.

**Q23: Data Chain Thinking** — A dose order references a site, which references a protocol, which references a partner. If we change the partner's status to INACTIVE, what downstream effects should we consider?

> **Expected**: Cascade thinking — active orders for that partner's sites, capacity reservations, pending approvals, notification recipients, protocol status. Must trace the full impact chain: partner → sites → protocols → orders → approvals → capacity → notifications.
>
> **Green flag**: Asks "do we have active orders for this partner's sites?" before proposing a solution.

**Q24: Debugging Approach** — Production shows a blank `changed_by` in the audit log for role assignment updates. Where do you start investigating?

> **Expected**: DB → BE → FE order:
> 1. Check the `audit_log` table — what's in `performed_by`? Is it empty string or NULL?
> 2. Check the DB trigger — is it reading `current_setting('app.current_user')`? Is the session variable set?
> 3. Check the service layer — is `setChangedBy()` called before `save()`? Is it inside or outside the `isDataChanged()` block?
> 4. Check `changed_on` timestamps — do they cluster? Points to a specific deployment or data migration.
>
> **Red flag**: "Start by checking the React component."

---

## Advanced Grilling — Spring Boot Deep Dive

> **Use when**: Candidate claims 10+ years Java/Spring. These verify depth vs surface knowledge.

**Q25: Transaction Scope Leak** — You use `@Transactional` on a service method that reads from DB, calls an external HTTP API (10 second timeout), then writes to DB. What's the problem?

> **Expected**: The DB connection is held open for the entire 10-second HTTP call. Under load, the connection pool is exhausted and the app stops serving requests. Fix: split into two methods — read + HTTP call outside the transaction, write inside its own `@Transactional`. Or use `TransactionTemplate` for programmatic control.
>
> **Red flag**: Doesn't mention connection pool exhaustion.

**Q26: Propagation** — What's the difference between `@Transactional(propagation = REQUIRED)` and `REQUIRES_NEW`? Give a real scenario where picking the wrong one causes data loss.

> **Expected**: `REQUIRED` (default) joins the existing transaction. `REQUIRES_NEW` suspends the outer and creates a new one. Scenario: Parent method saves an order, calls a child method with `REQUIRES_NEW` that logs an audit entry. If the parent rolls back after the child commits, the audit entry persists but the order doesn't — orphaned audit log.
>
> **Red flag**: Can't explain propagation beyond "it's the default."

**Q27: Clean Architecture in Spring Boot** — How do you prevent JPA annotations from leaking into your domain layer?

> **Expected**: Separate domain models (POJOs) from JPA entities. Use mappers at the boundary. Or accept the pragmatic trade-off: annotate domain objects with JPA but keep repository interfaces in the domain layer with implementations in infrastructure.
>
> **Green flag**: Acknowledges the pragmatic trade-off instead of being dogmatic.

**Q28: Long Service Methods** — Our `UserService.updateUser()` handles role assignments, group assignments, site assignments, and manufacturer assignments — all in one method, ~300 lines. A developer proposes splitting each into its own `@Transactional` method. Why is that dangerous?

> **Expected**: If role assignment succeeds but group assignment fails, you have a partially updated user with no way to roll back the roles. All related mutations must be in ONE transaction. Extract private helper methods for readability, but the `@Transactional` boundary must wrap the entire operation.
>
> **Bonus**: Mentions that `@Transactional` on private methods doesn't work (proxy-based AOP only intercepts public methods called from outside the class).

**Q29: Silent Save Failure** — `repository.save()` is called but the database row isn't updated. No exception thrown. The method is `@Transactional`. What happened?

> **Expected**: Multiple possibilities:
> 1. JPA dirty checking — entity wasn't actually changed, Hibernate won't issue an UPDATE
> 2. Entity is detached — `save()` merges it but the returned (managed) entity isn't used
> 3. Transaction is read-only (`@Transactional(readOnly = true)`)
> 4. Another `@Transactional(propagation = NOT_SUPPORTED)` suspended the transaction
>
> **Red flag**: Only says "check the logs."

**Q30: Constructor Bloat** — A service has 12 dependencies injected via constructor (`@RequiredArgsConstructor`). Code review — what do you say?

> **Expected**: 12 dependencies = Single Responsibility violation. The class is doing too much. Refactor: extract cohesive groups of dependencies into smaller services (e.g., `UserRoleService`, `UserGroupService`). The parameter count is a design smell, not a DI problem.
>
> **Red flag**: "It's fine, Lombok handles it."

**Q31: Optimistic Locking Details** — We have a `@Version` field. Two users load the same dose order (version=3). User A saves (version→4). User B saves. What exception is thrown and how do you handle it?

> **Expected**: `OptimisticLockException` (JPA) or `StaleObjectStateException` (Hibernate). Handle in `@ControllerAdvice` — return 409 Conflict: "This record was modified by another user. Please refresh and try again." Never expose the raw exception.

**Q32: Spring Version Awareness** — What changed between `javax.*` and `jakarta.*` packages in Spring Boot 3? Have you migrated across that boundary?

> **Expected**: Spring Boot 3 moved from `javax.persistence` → `jakarta.persistence`, `javax.servlet` → `jakarta.servlet`. Requires Java 17+ baseline. Every JPA/Servlet import changes. If they haven't done this migration, they've never used Spring Boot 3.
>
> **Use when**: Resume lists Spring 4 or old Spring versions.

---

## Advanced Grilling — Lazy Loading Deep Dive

> **Use when**: Candidate's JPA experience is unclear. These 6 questions escalate from basic to expert.

**Q33: Fundamentals** — What does `FetchType.LAZY` actually do under the hood?

> **Expected**: Hibernate returns a **proxy object** (or `PersistentCollection` for collections) instead of real data. The proxy intercepts the first access (e.g., `protocol.getSites().size()`) and fires a SELECT at that point — but ONLY if the Hibernate Session is still open. The collection field is NOT null — it's a special Hibernate wrapper that hasn't been initialized yet.
>
> **Red flag**: "It returns null until you access it."

**Q34: N+1 Problem** — You load 50 protocols, then iterate and call `protocol.getSites()` on each. How many SQL queries fire?

> **Expected**: **51 queries** — 1 for the 50 protocols, then 1 per protocol to load its sites. Fix options (should name at least 2):
> 1. `JOIN FETCH` in JPQL: `SELECT p FROM Protocol p JOIN FETCH p.sites`
> 2. `@EntityGraph(attributePaths = {"sites"})` on the repository method
> 3. `@BatchSize(size = 50)` on the collection — loads in batches
> 4. DTO projection — skip entity loading entirely
>
> **Red flag**: Only knows `FetchType.EAGER` as the fix.

**Q35: LazyInitializationException** — This code throws an exception. Why?

```java
@Service
public class ProtocolService {
    public ProtocolDTO getProtocol(Long id) {
        Protocol protocol = protocolRepository.findById(id).orElseThrow();
        ProtocolDTO dto = new ProtocolDTO();
        dto.setName(protocol.getName());
        dto.setSites(protocol.getSites().stream()    // 💥 BOOM
            .map(this::toSiteDTO)
            .collect(Collectors.toList()));
        return dto;
    }
}
```

> **Expected**: No `@Transactional` on the method. The Hibernate Session opened by `findById()` closes immediately. When `protocol.getSites()` is accessed, session is gone → `LazyInitializationException`.
>
> **Fix options**: (1) Add `@Transactional(readOnly = true)`. (2) `@EntityGraph(attributePaths = {"sites"})` on repo. (3) `JOIN FETCH` query.
>
> **Follow-up trap**: "Would `spring.jpa.open-in-view=true` fix it?" → Technically yes — keeps session open until HTTP response. But it's an anti-pattern: DB connections held during JSON serialization, hides N+1, unpredictable query timing. Should be `false`.

**Q36: Multiple Collection Fetch (Expert)** — A `Protocol` has `sites`, `approvers`, `products`, and `patients`. You write:

```java
@EntityGraph(attributePaths = {"sites", "approvers", "products", "patients"})
Optional<Protocol> findById(Long id);
```

What's the problem?

> **Expected**: **Cartesian product explosion.** Hibernate generates a single JOIN query. 10 sites × 5 approvers × 8 products × 3 patients = **1,200 rows** for one protocol. Hibernate deduplicates in memory, but the DB sends 1,200 rows over the wire.
>
> Also: `MultipleBagFetchException` if more than one `List` (bag) is fetched simultaneously.
>
> **Fix**: Fetch at most ONE collection via `JOIN FETCH`, load others via `@BatchSize` or separate queries. Best: multiple queries — 5 total instead of 1 cartesian, far less data transferred.
>
> **This is expert-level.** If they get this, they deeply understand JPA.

**Q37: Jackson + Lazy Loading Serialization Trap**

```java
@RestController
public class ProtocolController {
    @GetMapping("/protocols/{id}")
    public Protocol getProtocol(@PathVariable Long id) {
        return protocolService.findById(id);
    }
}
```

Two bugs. Name them.

> **Expected**:
>
> **Bug 1**: Returning entity directly — Jackson tries to serialize ALL fields including lazy collections. Either `LazyInitializationException` (session closed) or unexpected queries during serialization (with `open-in-view=true`).
>
> **Bug 2**: Violates layered architecture — entity structure leaks into API contract. Changing the entity changes the API. Services must return DTOs, entities never leave the service layer.

**Q38: Design the Data Access** — New endpoint returning 500 dose orders with protocol name and site name for a grid. Design the data access.

> **Expected**: Don't load entities at all. Use DTO projection:
> ```java
> @Query("SELECT new com.lilly.dto.OrderGridDTO(" +
>        "d.doseOrderNumber, d.status, p.protocolName, s.siteName) " +
>        "FROM DoseOrder d JOIN d.protocol p JOIN d.site s " +
>        "WHERE d.status != 'DELETED'")
> List<OrderGridDTO> findOrdersForGrid();
> ```
> One query, no lazy loading, no N+1, minimal data transfer.
>
> **Red flag**: Loads 500 full `DoseOrder` entities with `@EntityGraph` for a read-only grid.

### Lazy Loading Scoring

| Question | Tests | Must-pass? |
|----------|-------|------------|
| Q33 (proxy) | Basic understanding | Yes |
| Q34 (N+1) | Performance awareness | Yes |
| Q35 (LazyInitEx) | Practical debugging | Yes |
| Q36 (cartesian) | Advanced JPA | No — bonus |
| Q37 (serialization) | Architecture discipline | Yes |
| Q38 (DTO projection) | Design maturity | Yes |

**Pass: 4/6 including Q33, Q34, Q35.** If they get Q36, they're genuinely senior.

---

## Advanced Grilling — Kafka / Event-Driven

> **Use when**: Candidate lists Kafka, SQS, event-driven, or messaging on resume. Push strengths to the limit.

**Q39: Duplicate Events** — A Kafka consumer processes a "dose order approved" event and sends an email via SES. The SES call succeeds but the consumer crashes before committing the offset. What happens on restart?

> **Expected**: Message is redelivered. Email is sent again — duplicate. Fix: idempotency key (e.g., `orderId + eventType + timestamp` stored in DB). Check before sending. Or use outbox pattern — write to DB in same transaction as offset commit, separate process sends emails.
>
> **Green flag**: Mentions outbox pattern or idempotency key without prompting.

**Q40: SQS vs Kafka** — When would you pick SQS over Kafka for a notification system?

> **Expected**: SQS if: (1) no replay/reprocessing needed, (2) per-message visibility timeout (good for retries), (3) no ordering guarantees needed, (4) simpler ops (no broker). Kafka if: (1) event sourcing/replay, (2) high throughput, (3) multiple consumers of same stream.
>
> Our notification system is SES-based, fire-and-forget — SQS is actually the better fit.

**Q41: Write Conflict in Event-Driven** — Two services both update the same aggregate via events. How do you handle write conflicts?

> **Expected**: Single writer per aggregate (one service owns state). Others publish events, only the owner writes. Or: optimistic concurrency with version numbers in events. This is a depth check — vague answers suggest resume inflation.

**Q42: Lost Events** — A Kafka consumer committed the offset but the database write failed (connection timeout). Events were lost. How do you prevent this?

> **Expected**: Transactional outbox pattern: write to DB and outbox table in ONE transaction. Separate poller/CDC reads outbox and publishes to Kafka. Or: disable auto-commit, process → write to DB → manually commit offset (still has a failure window). Only truly safe: outbox pattern.

---

## Advanced Grilling — Database Blind Spots

> **Use when**: Candidate lists databases but no ORM/JPA/Flyway. Probing actual data access experience.

**Q43: Data Access Technology** — Your resume lists MySQL, PostgreSQL, Oracle — but doesn't mention how you access them. JPA/Hibernate? JDBC? MyBatis? Something else?

> **Direct probe.** Let them reveal actual experience. No escape.

**Q44: Persist vs Merge** — What's the difference between `EntityManager.persist()` and `EntityManager.merge()`?

> **Expected**: `persist()` makes a transient entity managed (INSERT). `merge()` copies state from a detached entity to a managed copy (UPDATE or INSERT). Calling `persist()` on an entity with an existing ID throws `EntityExistsException`.
>
> **If they don't know**: They haven't used JPA.

**Q45: Cascade + OrphanRemoval Trap** — `@OneToMany(cascade = ALL, orphanRemoval = true)`. You call `parent.getChildren().clear()` then `parent.getChildren().addAll(newChildren)`. What SQL does Hibernate generate?

> **Expected**: DELETE all existing children, then INSERT all new children — even the ones that existed before. IDs change, audit trail breaks. This is the CMCDOS-3150 anti-pattern.

**Q46: Hard Delete vs Soft Delete** — What's the difference between `DELETE FROM orders WHERE status = 'CANCELLED'` and `UPDATE orders SET status = 'DELETED' WHERE status = 'CANCELLED'` in a pharmaceutical system?

> **Expected**: Hard delete destroys the audit trail. In a regulated system (FDA, GxP), every state change must be traceable. Soft delete preserves the record for compliance, historical reporting, and reversal.

**Q47: Flyway Version Conflict** — Two developers create migration `V360__add_column.sql` on separate branches. Developer A merges first. Developer B merges. CI passes. What happens when the app starts?

> **Expected**: Flyway detects checksum conflict — V360 already applied with different content. App crashes/refuses to start. Fix: re-number to V361. Our CI catches this with a "Migration Check" — but only if branch is up-to-date.

**Q48: DB Trigger Investigation** — A database trigger logs every UPDATE to an audit table. The trigger captures `current_setting('app.current_user')`. But the audit log shows blank `performed_by`. Where's the bug?

> **Expected**: The application isn't setting the PostgreSQL session variable before the transaction. The Spring service needs to execute `SET LOCAL app.current_user = 'John Doe'` at transaction start, or the trigger reads empty/default.

---

## Advanced Grilling — React Depth Check

> **Use when**: Candidate is Angular-heavy or React experience is unclear.

**Q49: Angular vs React Mental Model** — You've used Angular with NgRx (Store, Actions, Reducers, Effects). In React, there's no built-in equivalent. How do you manage complex async state?

> **Expected**: Multiple options — (1) React Query/TanStack Query for server state, (2) Context + `useReducer` for local complex state, (3) Jotai/Zustand for global state. Should NOT say "I'd add Redux."
>
> **Red flag**: Reaches for `rxjs` patterns or `Subject`/`pipe`/`switchMap` — that's Angular brain.

**Q50: TanStack Query Optimistic Update** — We fetch dose orders with `useQuery`. User edits an order in a modal. How do you update the grid without refetching all 500 orders?

> **Expected**: Optimistic update via `queryClient.setQueryData()` — mutate cache directly, then `invalidateQueries` in background. Or use `useMutation` with `onMutate` for optimistic update and `onError` for rollback.

**Q51: React.memo Doesn't Work** — Grid has `React.memo`. Search field still causes re-render. Why?

> **Expected**: The `rows` prop is a new array reference on every render (filtering creates a new array). `React.memo` does shallow comparison — new reference = re-render. Fix: `useMemo` the filtered rows so reference is stable when data hasn't changed. Also debounce search input.
>
> **Red flag**: "Just use `useCallback`" — wrong tool (that's for functions, not data).

**Q52: Jotai Atom Bug** — This counter resets on every render. Why?

```tsx
const MyComponent = () => {
  const countAtom = atom(0);
  const [count, setCount] = useAtom(countAtom);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
};
```

> **Expected**: Atom is recreated on every render — it's a new instance each time. Atoms must be created OUTSIDE the component (module scope) or memoized with `useMemo`.

**Q53: React Version Check** — If resume lists an old React version (e.g., "React 14" or "React 16"):

> "React 14 is from 2015 and predates hooks entirely. React 16.8 introduced hooks. Did you mean a different version? Have you used hooks (`useState`, `useEffect`, `useMemo`, custom hooks) in production?"
>
> **Purpose**: Clarify resume accuracy. If they've never used hooks, they need significant ramp-up for our all-hooks codebase.

---

## Advanced Grilling — System Design / DMS Scenarios

> **Use when**: Assessing domain reasoning and system-level thinking.

**Q54: Approval Workflow State Machine** — Design this: A dose order is created by a site requester. Sequential approval from Clinical Supply, then parallel approval from Clinical Ops AND Manufacturer. If either parallel approver rejects → rejected. Both approve → approved.

> **Expected**: States: `PENDING_CS` → `PENDING_CO_MFG` → `APPROVED` / `REJECTED`
> - CS approves → `PENDING_CO_MFG`. CS rejects → `REJECTED`.
> - In `PENDING_CO_MFG`: must track CO and MFG independently.
> - Both approve → `APPROVED`. Either rejects → `REJECTED`.
>
> **Key**: The parallel step requires independent approval state tracking.

**Q55: Changing IDs Bug** — Bug report: "When I update a protocol and add a new approver, the existing approvers' IDs change." 30 seconds — hypothesize the root cause.

> **Expected**: The update method calls `collection.clear()` then `addAll(newSet)`. Hibernate's orphanRemoval deletes all existing rows, inserts everything as new with new auto-generated IDs. Fix: in-place reconciliation.
>
> **This is literally CMCDOS-3150.**

**Q56: NULL Audit Fields Investigation** — Production alert: `changed_by` is NULL for 47 rows in `user_roles`. Should never be NULL after UPDATE. App running 3 months. How do you investigate?

> **Expected**:
> 1. Check `audit_log` — do those 47 rows have entries? What's `performed_by`?
> 2. Query `changed_on` — do they cluster in time? Points to specific deployment or bulk operation.
> 3. Check service code — is `setChangedBy()` inside or outside `isDataChanged()`?
> 4. Check if a Flyway migration updated those rows without setting audit fields.
> 5. Check DB trigger — is there a `NULLIF` guard converting empty string to NULL?
>
> **Looking for**: Systematic, layered investigation. Not "just backfill them."

**Q57: Security — IDOR Vulnerability** — A developer writes:

```java
@GetMapping("/orders")
public List<OrderDTO> getOrders(@RequestParam String userId) {
    return orderService.findByUserId(userId);
}
```

What's the security flaw?

> **Expected**: **Insecure Direct Object Reference (IDOR)** — attacker changes `userId` to see another user's orders. Must use `SecurityUtils.getCurrentUserId()` from the authenticated session, NEVER from request parameters. OWASP Top 10.

**Q58: Cross-Tab Logout** — A user has the app open in 3 browser tabs. They log out in one tab. The other two tabs stay logged in. Why?

> **Expected**: Logout clears localStorage in one tab, but other tabs already loaded the token into React in-memory state (Context/AuthContext). They don't detect the localStorage change. Fix: listen for the `storage` event across tabs — when a logout key is set, all tabs should clear their auth state and redirect to login.

**Q59: S3 Path Traversal** — Our backend stores uploaded documents in S3:

```java
String key = request.getParameter("filename");
s3Client.putObject(bucket, key, inputStream);
```

What's the vulnerability?

> **Expected**: **Path traversal** — user-supplied filename could contain `../` or overwrite other files. Must sanitize/generate the key server-side. Also: no validation of file type, size, or content.

---

## Advanced Grilling — DMS Production Anti-Patterns (Checklist Sync)

> **Use when**: Every candidate. These 10 questions close the gap between the interview guide and the code review checklist. Each maps to a real production bug pattern (P1–P7) or a checklist layer that had zero interview coverage. The checklist pattern ID is noted for traceability.

**Q60: Hardcoded Audit User (Checklist P1)** — A developer writes a mapper that converts an external API response into a new entity:

```java
public Protocol toEntity(ExternalProtocolDTO dto) {
    Protocol entity = new Protocol();
    entity.setName(dto.getName());
    entity.setCreatedBy("SYSTEM");
    entity.setCreatedOn(LocalDateTime.now());
    return entity;
}
```

Code review — what do you flag?

> **Expected**: `"SYSTEM"` is hardcoded. Must use `SecurityUtils.getCurrentUserId()` or `getCurrentUserDisplayName()` — even in mappers and converters. This pattern caused 6 production tickets in R1.2.1. The only time `"SYSTEM"` is acceptable is in Flyway migration backfills where no HTTP context exists.
>
> **Red flag**: "SYSTEM is fine for automated processes."

**Q61: Conditional Audit Stamps (Checklist P3)** — A developer writes:

```java
public void updateProtocol(ProtocolDTO dto) {
    Protocol existing = repo.findById(dto.getId()).orElseThrow();
    existing.setChangedBy(SecurityUtils.getCurrentUserId());
    existing.setChangedOn(LocalDateTime.now());
    existing.setName(dto.getName());
    if (isDataChanged(dto, existing)) {
        repo.save(existing);
    }
}
```

Two bugs. Name them.

> **Expected**:
>
> **Bug 1 (P5)**: `isDataChanged()` called AFTER setters — entity already matches DTO, always returns false. (Same as Q5.)
>
> **Bug 2 (P3)**: `setChangedBy`/`setChangedOn` are OUTSIDE the `isDataChanged()` gate. Even if fixed to compare-before-mutate, the audit stamps must only be set when data actually changed — otherwise "last modified" updates on every view/save even with no changes. This caused 4 production tickets.
>
> **Correct pattern**:
> ```java
> if (isDataChanged(dto, existing)) {
>     existing.setName(dto.getName());
>     existing.setChangedBy(SecurityUtils.getCurrentUserId());
>     existing.setChangedOn(LocalDateTime.now());
>     repo.save(existing);
> }
> ```

**Q62: Child→Parent Audit Propagation (Checklist CMCDOS-2896)** — A user modifies an approver on a protocol (child entity). The approver's `changed_by` updates correctly. But the protocol's (parent) `changed_by` stays as the original creator. Is this a bug?

> **Expected**: YES. When a child entity changes, the parent's `changed_by`/`changed_on` MUST also update. Otherwise, querying "who last modified this protocol?" gives a wrong answer — it shows the creator, not the person who changed the approver. The reverse is NOT true: parent-only changes must NOT cascade to children.
>
> **Follow-up**: "What about adding a NEW child?" → New children get `created_by` only (not `changed_by`). But the parent still gets `changed_by`/`changed_on` updated.
>
> **This is CMCDOS-2896 — a real pattern we enforce in code review.**

**Q63: Frontend createdOn Leak (Checklist P4)** — Bug report: "When I add a new approver to an existing protocol, the new approver's `createdOn` shows yesterday's date instead of today." Root cause?

> **Expected**: The frontend is copying `createdOn` from an existing approver (or the parent protocol) into the new approver's DTO. When `id` is undefined/null (new entity), the frontend must NOT send `createdOn` or `createdBy` — the backend sets these from `SecurityUtils` and `LocalDateTime.now()`. The fix: clear audit fields when `id` is null before submitting.
>
> **Red flag**: "Backend should just ignore the frontend's createdOn." — That's defense-in-depth but the frontend must not send it in the first place.

**Q64: UTC DateTime Contract (Checklist P7 / Layer 5)** — Backend returns a `LocalDateTime` field: `"2026-05-13T20:33:49"`. Frontend does `new Date("2026-05-13T20:33:49")`. User is in EST (UTC-5). What date/time does the user see?

> **Expected**: Without a `Z` suffix, `new Date()` treats it as **local time** (EST). The user sees `2026-05-13 20:33:49 EST` = `2026-05-14 01:33:49 UTC`. But the backend meant UTC! So the displayed time is 5 hours wrong. Fix: frontend must append `Z` before parsing: `new Date(str + 'Z')`, or use the centralized `dateUtils.ts` which handles this.
>
> **Follow-up**: "For date-only fields like `calibrationDate`, what happens if you use `.toISOString()`?" → `.toISOString()` converts to UTC. A date entered as `2026-05-13` in EST becomes `2026-05-13T05:00:00Z` → the API receives `2026-05-13` or `2026-05-14` depending on time of day. Must use `formatDateForApi()` which extracts `YYYY-MM-DD` without timezone conversion.
>
> **This is a live bug pattern — our checklist grep for `new Date(` outside `dateUtils.ts` is a CI warning.**

**Q65: Stale Closure Trap (Checklist CMCDOS-2339)** — This React code has a bug. The `handleSave` always sends the OLD value:

```tsx
const [status, setStatus] = useState('PENDING');

const handleChange = (newStatus: string) => {
  setStatus(newStatus);
  handleSave(status); // 🐛
};
```

Why?

> **Expected**: `setStatus` is async — `status` still holds the old value in the same render cycle. `handleSave(status)` sends `'PENDING'` even after `setStatus('APPROVED')`. Fix: pass `newStatus` directly: `handleSave(newStatus)`. Or use `useEffect` to react to state changes.
>
> **Follow-up**: "What about inside a `setInterval` callback?" → The callback captures the closure at creation time. Use `useRef` for mutable values that need to be current inside intervals/timers.
>
> **This is CMCDOS-2339.** The checklist mandates: never read state in the same callback after `setState`.

**Q66: System-Wide Sibling Audit (Checklist Layer 8)** — You fix a `clear()+addAll()` bug in `ProtocolService.updateProtocol()`. Your PR has the fix + tests. Code review — what's missing?

> **Expected**: A **system-wide sibling audit**. Before the PR is complete, you must grep ALL other services for the same anti-pattern:
> ```
> grep -rn '\.clear()\|\.removeAll' --include='*Service.java' src/
> ```
> Check: `UserService`, `PartnerService`, `DoseOrderService`, `RAMLicenseServiceImpl` — do they have the same `clear()+addAll()` pattern on their child collections? If yes, fix all in the same PR or create follow-up tickets. Document in PR description: "System-wide audit: checked N services, found M additional instances."
>
> **This is the meta-lesson from R1.2.1**: 42 bug tickets would have been ~6 if system-wide audits had been mandatory. Our checklist (Layer 8) now requires this for every PR.
>
> **Green flag**: Candidate mentions "I'd check if the same pattern exists elsewhere" without being prompted.

**Q67: 6-Layer Field Completeness (Checklist Layer 6.2)** — You add a new column `backup_dose_order_number BIGINT` to the `dose_orders` table. Walk me through every file that must change.

> **Expected** (all 6 layers):
> 1. **DB**: Flyway migration `V{N}__CMCDOS_XXXX_add_backup_order_number.sql`
> 2. **Entity**: `DoseOrder.java` — `@Column(name = "backup_dose_order_number") private Long backupDoseOrderNumber;`
> 3. **DTO**: `DoseOrderDTO.java` — `private Long backupDoseOrderNumber;`
> 4. **Mapper**: `DoseOrderMapper.java` — map entity↔DTO
> 5. **Frontend type**: `DoseOrderDTO.ts` — `backupDoseOrderNumber: number | null;`
> 6. **Frontend display**: Grid column or detail view renders the field
>
> **Naming chain**: DB `backup_dose_order_number` → Java `backupDoseOrderNumber` → JSON `backupDoseOrderNumber` → TS `backupDoseOrderNumber` — must match exactly, no `@JsonProperty` aliasing.
>
> **Red flag**: Misses the mapper, or suggests different names at different layers.

**Q68: @Enumerated Trap (Checklist Layer 2.3)** — Entity uses `@Enumerated(EnumType.ORDINAL)` for a status field. The enum has `PENDING(0), APPROVED(1), REJECTED(2)`. A developer adds `CANCELLED` between `APPROVED` and `REJECTED`. What breaks?

> **Expected**: `ORDINAL` stores the enum's position (0, 1, 2). After adding `CANCELLED` at position 2, existing `REJECTED` rows (stored as `2`) now map to `CANCELLED`. All rejected orders silently become cancelled. Data corruption with no error.
>
> **Fix**: Always use `@Enumerated(EnumType.STRING)` — stores `"PENDING"`, `"APPROVED"`, `"REJECTED"` as text. Immune to reordering. Our checklist blocks `EnumType.ORDINAL` in code review.

**Q69: AbortController / Stale Response (Checklist FE §4.6)** — User clicks "Load Orders", then immediately navigates to another page. The API response arrives after navigation. What happens? How do you prevent it?

> **Expected**: The response handler tries to update state on an unmounted component. In React 18, this doesn't throw (React silently ignores), but it wastes resources and can cause subtle bugs if it triggers side effects. Fix:
> ```tsx
> useEffect(() => {
>   const controller = new AbortController();
>   fetchOrders({ signal: controller.signal }).then(setOrders);
>   return () => controller.abort();
> }, []);
> ```
> The `AbortController` cancels the in-flight request on unmount. Alternatively, use a `let ignore = false` flag in the cleanup.
>
> **Green flag**: Mentions `AbortController` without prompting.

**Q70: Silent Filtering Failure / Enum Attribute Converter Casing (Checklist Layer 2.3)** — We use a custom JPA `@Converter(autoApply = true)` that maps a Java enum (e.g., `EntityStatus.ACTIVE`) to a database string. On database read, it converts case-insensitively. However, when Hibernate serializes parameter values for a JPQL query (e.g. `where lr.status = :status`), it binds the exact converted string (e.g. `'Active'`). If database rows contain `'ACTIVE'` in all-caps, the query returns an empty list `[]` without throwing any error. Why does this happen, and how do you resolve and prevent it?

> **Expected**: 
> 1. **Root Cause**: The read converter is case-insensitive, masking data discrepancies. The write/serialize step is case-sensitive, emitting `'Active'`. PostgreSQL executes case-sensitive comparisons, so `'ACTIVE' = 'Active'` is false, resulting in silent filtering failures.
> 2. **Resolution**: Normalization migration (`UPDATE logistic_records SET status = 'Active' WHERE status = 'ACTIVE';`) and database-level CHECK constraints (`ALTER TABLE logistic_records ADD CONSTRAINT chk_logistic_records_status CHECK (status IN ('Active', 'Inactive'));`).
> 3. **Prevention**: Database-level constraints are the single source of truth for casing validation, not just ORM converters.
>
> **Green flag**: Identifies that case-insensitive reading masks database-level casing inconsistencies.

**Q71: Pod Startup Timeout in Service Mesh (Checklist DevOps / Layer 8)** — A newly deployed React frontend or Spring Boot backend pod goes into a crash loop. The OpenShift logs show health probe failures with HTTP 500 or timeout (`context deadline exceeded`). The application container logs show it started successfully. Under the hood, Istio sidecar injection is enabled. What is the root cause, and how do you configure the manifests to resolve this race?

> **Expected**: 
> 1. **Root Cause**: Istio pilot-agent intercepts Kubernetes liveness/readiness probes. If the application container attempts to handle health probes or starts before the `istio-proxy` sidecar has completed its control plane handshake and cert load, the proxy returns HTTP 500 or times out.
> 2. **Resolution**: Add the pod annotation `proxy.istio.io/config: '{ "holdApplicationUntilProxyStarts": true }'` under `spec.template.metadata.annotations`. This forces Kubernetes to delay the primary application container startup until the proxy container is fully ready.
>
> **Green flag**: Explains the interaction between Kubelet health probes, the Istio proxy sidecar, and the application container.

**Q72: CRI-O Container Runtime Saturation (Checklist DevOps)** — During deployment rollouts, OpenShift events show pods stuck in `ContainerCreating` with errors like `CRI-O due to system load... name is reserved` and health probe timeouts. What does this indicate, and how do you remediate it?

> **Expected**: 
> 1. **Root Cause**: Node-level CPU or Disk I/O resource saturation. The container runtime (CRI-O) is too slow to respond, causing the Kubelet container creation request to timeout. Kubelet retries, but because the previous request didn't finish cleaning up or registering, CRI-O throws a name collision error.
> 2. **Remediation**: Reschedule the pod to another node (delete/drain), increase health probe timeouts (`initialDelaySeconds`, `timeoutSeconds`, `failureThreshold`), and enforce strict CPU/Memory request and limit allocations to prevent node overcommit.
>
> **Green flag**: Recognizes this as a node-level hardware/runtime saturation issue rather than an application-specific code bug.

**Q73: Direct Repository Access from Controllers (Checklist Layer 2.1)** — During code review, you find a REST controller injecting a JPA repository directly to fetch records instead of calling a service (e.g. `RAMLicenseController` querying `UserRepository`). The developer argues, "It's a simple GET by ID with no business logic, so adding a service method is just boilerplate." What architectural risks does this present, and what is our design standard?

> **Expected**: 
> 1. **Bypasses Cross-Cutting Concerns**: Service layers handle transactional boundaries (`@Transactional`), security checks/validation (`@PreAuthorize`), and business audit logging. Direct controller-repository calls bypass these entirely.
> 2. **Violates Layered Isolation**: Tightly couples the controller to the persistence schema. If query logic or entity fetching strategy changes, the controller breaks.
> 3. **Strict Unidirectional Flow**: Our standard mandates `Controller → Service → Repository → Database`. Controllers must only invoke services, and services must return DTOs, not raw entities.
>
> **Green flag**: Recognizes that direct repository access bypasses service-level transactions or authorization checks.

**Q74: Query Index Bypass via Function-Wrapping (Checklist Layer 1.3 / DB Performance)** — In `CapacityReservationRepository`, a query matches dates using: `WHERE CAST(cr.requestedCalibrationDate AS DATE) = :inputDate`. The `requested_calibration_date` column is already a `DATE` column in Postgres and has a B-Tree index. Why is this query problematic, and how do you optimize it?

> **Expected**: 
> 1. **Root Cause**: Wrapping an indexed column inside a SQL function or typecast (like `CAST(...)`, `LOWER(...)`, or `CONCAT(...)`) in a `WHERE` clause forces PostgreSQL to abandon the B-Tree index and run a full-table sequential scan, evaluating the expression for every row.
> 2. **Optimization**: Remove the redundant cast and compare directly: `cr.requestedCalibrationDate = :inputDate`. If function-based filtering is truly required, a dedicated functional/expression index must be created on the database.
>
> **Green flag**: Explains that Postgres cannot use a standard index on a column if that column is modified by a function in the comparison.

**Q75: In-Memory Pagination OOM Risk (Checklist Layer 2.8 / DB Performance)** — A repository query filters protocols and fetches their approvers collection using:
```java
@Query("SELECT p FROM Protocol p LEFT JOIN FETCH p.approvers WHERE p.status = :status")
Page<Protocol> findByStatus(@Param("status") EntityStatus status, Pageable pageable);
```
During startup, Hibernate logs: `HHH000104: firstResult/maxResults specified with collection fetch; applying in memory!`. What is the danger of this query, and how do you optimize it?

> **Expected**: 
> 1. **Root Cause**: When joining a `@OneToMany` collection (`approvers`), the database result set duplicates parent rows. SQL-level pagination (`LIMIT` / `OFFSET`) would truncate child lists, so Hibernate pulls **all** matching records into the JVM heap and performs pagination in memory.
> 2. **Production Risk**: High risk of JVM Out-of-Memory (OOM) crash under production data load.
> 3. **Optimization**: Paginate the query without joining the collection first (fetch parent IDs), then load the associated collections in a secondary batch load (using `IN` or `@BatchSize`).
>
> **Green flag**: Identifies that collection fetch joins with pagination result in Hibernate fetching the entire table into memory.

**Q76: Multiple Collection Fetch Cartesian Explosion (Checklist Layer 2.3 / DB)** — You need to load a user along with their role, group, site, and manufacturer assignments. A developer writes:
```java
@Query("SELECT u FROM User u LEFT JOIN FETCH u.roleAssignments LEFT JOIN FETCH u.groupAssignments LEFT JOIN FETCH u.siteAssignments LEFT JOIN FETCH u.manuAssignments")
```
Why does Hibernate throw a `MultipleBagFetchException` or create a Cartesian product, and what is the best practice to load these relationships?

> **Expected**: 
> 1. **MultipleBagFetchException**: Hibernate throws this to prevent Cartesian product explosion when fetching more than one unordered `List` (bag) collection in a single query.
> 2. **Cartesian Product**: If a user has 4 roles, 4 groups, 4 sites, and 4 manufacturer assignments, a single JOIN query returns `4 * 4 * 4 * 4 = 256` rows of redundant data over the network, which Hibernate must deduplicate in memory.
> 3. **Resolution**: Split the load into separate sequential queries inside a single `@Transactional` session (e.g., query the user, then query/initialize each collection separately), or use `@BatchSize` on collections.
>
> **Green flag**: Mentions that fetching multiple collections concurrently results in a Cartesian product multiplication of rows over the network.

**Q77: Frontend Date Library Bloat and Timezone Offset (Checklist FE §4.5 / Layer 5)** — In our frontend codebase, we have files importing `moment`, others importing `date-fns`, and others importing `dayjs`. What problems does this cause, and how do we prevent timezone offsets when submitting dates to the backend API?

> **Expected**: 
> 1. **Bundle Size Bloat**: Having multiple overlapping date libraries (`moment`, `date-fns`, `dayjs`) adds unnecessary package size. We must standardize on a single modern, lightweight library (like `dayjs`) and configure ESLint to block other imports.
> 2. **Timezone Offset Bugs**: The default `.toISOString()` formats date-times in UTC. If a user selects a date (e.g., `2026-07-02` in EST) and it gets converted to UTC, it might shift to the previous day (`2026-07-01T23:00:00Z`). We must use a centralized utility (like `formatDateForApi()`) in our shared `dateUtils.ts` to extract the literal `YYYY-MM-DD` string without timezone shifting.
>
> **Green flag**: Explains how timezone offsets can shift dates to the previous/next day when converting local dates to ISO strings.

**Q78: Type Safety vs TypeScript 'any' (Checklist FE §4.3)** — We have over 200+ instances of `: any` declarations in our React codebase (e.g., `roleAssignments: any[]` in `ProfileService.ts`). Why is this dangerous in a clinical system, and what is our coding standard for type declarations?

> **Expected**: 
> 1. **Loses Type Safety**: The `any` type disables the TypeScript compiler's static analysis, making the code equivalent to raw JavaScript. Any syntax errors, renamed properties, or missing properties will not be caught at compile-time and will cause runtime crashes.
> 2. **Our Standard**: Explicitly declare strict TypeScript `interfaces` or `types` for all component props, API payloads, and state models. Never use `any`. Add the `noImplicitAny` compiler option and configure ESLint to warn or error on the use of `any` in CI build gates.
>
> **Green flag**: Emphasizes that compile-time checks are the first line of defense against production crashes in regulated systems.

### DMS Anti-Patterns Scoring

| Question | Checklist Pattern | Must-pass? |
|----------|-------------------|------------|
| Q60 (hardcoded SYSTEM) | P1 — 6 production tickets | Yes |
| Q61 (conditional audit) | P3 + P5 — 6 production tickets | Yes |
| Q62 (child→parent audit) | CMCDOS-2896 | No — DMS-specific |
| Q63 (createdOn leak) | P4 — 1 production ticket | No — DMS-specific |
| Q64 (UTC datetime) | P7 / Layer 5 | Yes |
| Q65 (stale closure) | CMCDOS-2339 | Yes |
| Q66 (sibling audit) | Layer 8 | Yes |
| Q67 (6-layer completeness) | Layer 6.2 | Yes |
| Q68 (@Enumerated) | Layer 2.3 | Yes |
| Q69 (AbortController) | FE §4.6 | No — bonus |
| Q70 (converter casing) | Layer 2.3 / Case Drift | Yes |
| Q71 (Istio sidecar race) | DevOps / Service Mesh | Yes |
| Q72 (CRI-O saturation) | DevOps / Container Runtime | No — advanced |
| Q73 (direct repo calls) | Layer 2.1 / TD-06 | Yes |
| Q74 (cast index bypass) | Layer 1.3 / DB Perf | Yes |
| Q75 (in-memory paging) | Layer 2.8 / DB Perf | Yes |
| Q76 (multiple collections) | Layer 2.3 / DB Fetch | Yes |
| Q77 (date library bloat) | FE §4.5 / UTC Date | Yes |
| Q78 (loose TypeScript types) | FE §4.3 / type-safety | Yes |

**Pass: 12/19 including Q60, Q61, Q64, Q65, Q67, Q68, Q70, Q71, Q73, Q74, Q75, Q76, Q78.**

---

## Resume Weak-Area Probes

> Use these to probe specific gaps per candidate. Check the resume for these common DMS-critical gaps:

### Gap: No JPA/Hibernate Listed
- Q43 (data access technology), Q44 (persist vs merge), Q33 (LAZY proxy), Q34 (N+1), Q45 (cascade trap)

### Gap: No Flyway/Migrations Listed
- Q10 (idempotency), Q11 (NOT NULL column), Q47 (version conflict)

### Gap: No AWS Listed
- "How would you approach learning AWS SES, S3, SNS for this project?"
- Q59 (S3 path traversal — tests security even without AWS experience)

### Gap: No Security Mentioned
- Q17 (route guards), Q22 (security mindset), Q57 (IDOR), Q59 (path traversal)
- "Your resume doesn't mention auth. Have you implemented authentication/authorization? What approach?"

### Gap: Outdated Spring ("Spring 4" or no Boot)
- Q32 (javax→jakarta), Q25 (transaction scope), plus: "Name two Java 17+ features you use daily" (records, sealed classes, pattern matching, text blocks, virtual threads)

### Gap: Angular-Heavy / React-Unclear
- Q49 (Angular→React mental model), Q51 (React.memo), Q52 (Jotai atom), Q53 (React version check)

### Gap: No Regulated Industry
- Q8 (audit columns), Q9 (soft delete), Q46 (hard vs soft delete), Q24 (debugging blank audit)

---

## Scoring Rubric

### Standard Interview (Phases 1–6, 24 questions)

| Rating | Criteria |
|--------|----------|
| **Strong Hire** | 18+/24 correct, demonstrates security awareness, understands audit/compliance, asks thoughtful domain questions |
| **Hire** | 14-17/24 correct, solid on backend OR frontend (not both), shows willingness to learn the weaker area |
| **Borderline** | 10-13/24, knows fundamentals but gaps in advanced patterns. Consider if mentoring bandwidth exists |
| **No Hire** | Below 10, or any red flag triggered |

### Extended Interview (with Advanced Grilling)

| Section | Questions | Pass Threshold |
|---------|-----------|----------------|
| Phases 1–6 (core) | Q1–Q24 | 14/24 |
| Spring Boot deep dive | Q25–Q32 | 6/8 if claiming 10+ years |
| Lazy Loading | Q33–Q38 | 4/6 including Q33, Q34, Q35 |
| Kafka/Events | Q39–Q42 | 3/4 if it's their stated specialty |
| Database blind spots | Q43–Q48 | 2/6 (gap area — 2+ shows learnability) |
| React depth | Q49–Q53 | 3/5 |
| System design / DMS | Q54–Q59 | 4/6 |
| **DMS anti-patterns** | **Q60–Q78** | **12/19 including Q60, Q61, Q64, Q65, Q67, Q68, Q70, Q71, Q73, Q74, Q75, Q76, Q78** |

### Red Flags (Automatic No Hire)
- Suggests putting business logic in controllers
- Doesn't understand why backend must enforce security independently of frontend
- Can't explain what `@Transactional` does
- Suggests `SELECT *` or string concatenation in SQL queries
- No awareness of audit trail importance in regulated systems
- Says "frontend route guards are sufficient for security"
- Recommends `FetchType.EAGER` as a solution to lazy loading issues
- Says `"SYSTEM"` is acceptable as `createdBy` in application code (P1)
- Uses `@Enumerated(EnumType.ORDINAL)` (Q68)
- Can't explain why `setState` + immediate read gives stale value (Q65)

### Green Flags (Bonus Points)
- Asks about the approval workflow before answering design questions
- Mentions OWASP Top 10 unprompted
- Talks about idempotency in migrations without being asked
- Spots the set-before-compare bug (Q5) immediately
- Mentions the outbox pattern for event-driven reliability
- Mentions `MultipleBagFetchException` when discussing multiple collection fetching
- Asks about on-call/incident response process
- Says "I'd check if the same pattern exists elsewhere" before fixing a bug (Q66 — Layer 8)
- Knows `AbortController` for unmount cleanup without prompting (Q69)
- Mentions `EnumType.STRING` as the only acceptable option (Q68)
- Asks "does the parent's audit trail update when children change?" (Q62)

---

## Candidate Questions to Prepare For

They'll likely ask:
1. What does the team structure look like? (team size, time zones)
2. What's the deployment cadence? (sprint-based, sprint branches → main)
3. What's the on-call situation? (rotation, SLA)
4. What's the tech debt situation? (~1200 ESLint warnings, ~187 TS errors — be honest)
5. What's the biggest challenge right now? (R2.0 feature delivery + R1.2 hotfix maintenance in parallel)
6. What does the first 30/60/90 days look like?
7. What CI/CD pipeline do you use? (GitHub Actions — 5 required checks)
8. How do you handle database schema changes? (Flyway, currently at V359+)
9. How large is the database? (59 tables, 800+ orders in DEV)
10. What's the frontend testing story? (Playwright E2E + unit tests via Vitest)

---

## 30/60/90 Day Onboarding Suggestion

| Period | Focus |
|--------|-------|
| **Week 1-2** | Local setup (Docker, DB, IDE), read architecture docs, pair with team on small bug fix |
| **Week 3-4** | Solo bug fix with full DB→BE→FE flow, first PR through CI pipeline |
| **Month 2** | Own a small feature end-to-end, learn the approval workflow, contribute to code reviews |
| **Month 3** | Lead a feature implementation, participate in sprint planning, mentor-ready on one subsystem |

---

## Appendix: Checklist ↔ Interview Cross-Reference

> Maps each code review checklist pattern to its interview question(s). Gaps marked with ⚠️ are covered by onboarding, not interview.

| Checklist Pattern | ID | Interview Q | Coverage |
|-------------------|----|-------------|----------|
| Constructor injection only | Layer 2.1 | Q1 | ✅ |
| Controllers: no business logic | Layer 2.1 | Q2 | ✅ |
| Services return DTOs, not entities | Layer 2.1 | Q2, Q37 | ✅ |
| FetchType.LAZY always | Layer 2.3 | Q3, Q33–Q36 | ✅ |
| @Transactional correctness | Layer 2.6 | Q4, Q25, Q26, Q28, Q35 | ✅ |
| Set-before-compare (P5) | Layer 3 | Q5, Q61 | ✅ |
| Optimistic locking | — | Q6, Q31 | ✅ |
| Error response contract | Layer 2.4 | Q7 | ✅ |
| Audit columns NULL on INSERT | Layer 1.3 | Q8 | ✅ |
| Soft delete only | Layer 1.3 | Q9, Q46 | ✅ |
| Flyway idempotency | Layer 1.2 | Q10 | ✅ |
| NOT NULL column migration | — | Q11 | ✅ |
| clear()+addAll() anti-pattern (P2) | Layer 3 | Q12, Q45, Q55 | ✅ |
| Route guards ≠ security | Layer 7.1 | Q17, Q22 | ✅ |
| IDOR vulnerability | Layer 7.1 | Q57 | ✅ |
| N+1 query detection | Layer 2.8 | Q34 | ✅ |
| DTO projection for grids | — | Q38 | ✅ |
| Hardcoded "SYSTEM" (P1) | Layer 3 | **Q60** | ✅ NEW |
| Unconditional setChangedOn (P3) | Layer 3 | **Q61** | ✅ NEW |
| Child→parent audit (CMCDOS-2896) | Layer 7.2 | **Q62** | ✅ NEW |
| Frontend createdOn leak (P4) | Layer 3 | **Q63** | ✅ NEW |
| UTC DateTime contract (P7) | Layer 5 | **Q64** | ✅ NEW |
| Stale closure (CMCDOS-2339) | FE §4.7 | **Q65** | ✅ NEW |
| System-wide sibling audit | Layer 8 | **Q66** | ✅ NEW |
| 6-layer field completeness | Layer 6.2 | **Q67** | ✅ NEW |
| @Enumerated(STRING not ORDINAL) | Layer 2.3 | **Q68** | ✅ NEW |
| AbortController cleanup | FE §4.6 | **Q69** | ✅ NEW |
| Attribute Converter Case Drift | Layer 2.3 | **Q70** | ✅ NEW |
| Istio sidecar startup race | DevOps | **Q71** | ✅ NEW |
| CRI-O Node Saturation | DevOps | **Q72** | ✅ NEW |
| Direct Repository access from controllers | Layer 2.1 | **Q73** | ✅ NEW |
| Index bypass via function-wrapping | Layer 1.3 | **Q74** | ✅ NEW |
| In-memory pagination check | Layer 2.8 | **Q75** | ✅ NEW |
| Multiple collection fetch cartesian check | Layer 2.3 | **Q76** | ✅ NEW |
| Frontend date timezone conversion | FE §4.5 | **Q77** | ✅ NEW |
| TypeScript strict type check (no any) | FE §4.3 | **Q78** | ✅ NEW |
| @Transactional on getNextId() (P6) | Layer 3 | Q4 (partial) | ⚠️ onboarding |
| @Valid on @RequestBody | Layer 2.2 | — | ⚠️ onboarding |
| @ToString(exclude) on lazy | Layer 2.3 | — | ⚠️ onboarding |
| @EqualsAndHashCode(business key) | Layer 2.3 | — | ⚠️ onboarding |
| FK column needs index (PG) | Layer 1.3 | — | ⚠️ onboarding |
| COMMENT ON TABLE mandatory | DB §3.1 | — | ⚠️ onboarding |
| Migration naming convention | Layer 1.1 | Q20, Q47 | ✅ |
| Backfill 13-item checklist | DB §4.5 | — | ⚠️ onboarding |
| DISABLE TRIGGER ALL banned (RDS) | DB §2.9 | — | ⚠️ onboarding |
| PERSONA_BUTTON_ACCESS | FE §4.3 | — | ⚠️ onboarding |
| No prop drilling > 2 levels | FE §4.5 | — | ⚠️ onboarding |
| Layout/spatial anchoring (2518) | FE §4.13 | — | ⚠️ onboarding |
| Parent-child 10-scenario matrix | Appendix B | Q12 (partial) | ⚠️ onboarding |
| CORS: never * in production | Security | — | ⚠️ onboarding |
| console.log → logger.ts | FE §4.2 | — | ⚠️ onboarding |
| Check duplicates before insert | Layer 2.6 | — | ⚠️ onboarding |
| Methods ≤ 30 lines | Layer 2.9 | — | ⚠️ onboarding |
| Optional: return type only | Layer 2.12 | — | ⚠️ onboarding |

**Summary**: 39/51 patterns covered by interview (76%). Remaining 12 are convention/process items covered during onboarding week 1–2.
