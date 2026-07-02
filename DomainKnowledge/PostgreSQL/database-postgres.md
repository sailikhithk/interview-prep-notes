# PostgreSQL & Migrations Interview Prep Notes

This section covers database schema design, Flyway migration patterns, auditing mechanisms, and concurrency control in PostgreSQL.

---

## 1. Audit Trail Schema Design: Columns & Principles

### Standard Audit Structure
In GxP/regulated environments (like Dose Management Systems), every modification to master data must be auditable. A typical entity has four standard metadata columns:

| Column Name | Type | Value on INSERT | Value on UPDATE |
|---|---|---|---|
| `created_on` | `TIMESTAMP` | `CURRENT_TIMESTAMP` | Unchanged (Keep original value) |
| `created_by` | `VARCHAR` | Current user ID | Unchanged (Keep original value) |
| `changed_on` | `TIMESTAMP` | **NULL** | `CURRENT_TIMESTAMP` |
| `changed_by` | `VARCHAR` | **NULL** | Current user ID |

### Crucial Bug Spotting
> **Why should `changed_on` and `changed_by` be NULL on INSERT?**
>
> If they are set during the initial insert, it is impossible to distinguish between a record that has **never** been updated since creation, and one that was updated to the exact same values at the millisecond of creation. It pollutes historical change analytics and violates clean auditing practices.

---

## 2. Parent-Child Collection Reconciliation in JPA

### Problem Statement
When updating a parent record with a list of child records (e.g. Protocol with child Sites), how should the collections be reconciled in JPA?

### Anti-Pattern: `clear() + addAll()`
```java
// Avoid this:
parent.getChildren().clear();
parent.getChildren().addAll(newChildren);
```
*   **Resulting Queries**: Hibernate issues a `DELETE FROM child WHERE parent_id = ?` for **all** children, followed by `INSERT INTO child ...` for each child in the list.
*   **Consequences**:
    1.  New primary key IDs are generated for every child, breaking foreign keys.
    2.  Breaks audit triggers because old entities are destroyed and recreated.
    3.  Causes massive sequence/ID fragmentation.

### Pattern: In-Place Reconciliation
```java
// Prefer this:
public void reconcileChildren(Parent parent, List<ChildDto> newChildDtos) {
    // 1. Map existing children by ID
    Map<Long, Child> existingChildrenMap = parent.getChildren().stream()
            .collect(Collectors.toMap(Child::getId, Function.identity()));
            
    List<Child> updatedChildren = new ArrayList<>();
    
    for (ChildDto dto : newChildDtos) {
        if (dto.getId() != null && existingChildrenMap.containsKey(dto.getId())) {
            // Update existing child in-place
            Child child = existingChildrenMap.get(dto.getId());
            child.setName(dto.getName());
            updatedChildren.add(child);
        } else {
            // Insert new child (ID is null)
            Child child = new Child();
            child.setName(dto.getName());
            child.setParent(parent);
            updatedChildren.add(child);
        }
    }
    
    // 2. Clear and set back, letting orphanRemoval handle removals
    parent.getChildren().clear();
    parent.getChildren().addAll(updatedChildren);
}
```

---

## 3. Flyway Migrations: Idempotency & Conflict Resolution

### The "Version Conflict" Problem
If two developers create new migrations on their local branches with the same version number:
1.  Developer A creates `V247__add_status.sql`
2.  Developer B creates `V247__add_index.sql`

When merged into the sprint branch, the CI/CD pipeline will fail on the migration check.
*   **Fix**: Rename the local migration to the next available sequential number (e.g., `V248__add_index.sql`).
*   **Prevention**: Always pull and update your base branch before generating a new versioned migration script.

### Idempotency Principles
Migrations must be written so they can be re-run safely even if they fail midway:
-   **Add Column**: Use `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...`
-   **Drop Column**: Use `ALTER TABLE ... DROP COLUMN IF EXISTS ...`
-   **Triggers/Functions**: Always use `CREATE OR REPLACE FUNCTION ...` and drop/recreate triggers.

---

## 4. Production Schema Changes: The 500K Row Lock Risk

### Problem Statement
How do you safely add a `NOT NULL` column with a default value to a table containing 500K+ rows in production without causing table locks?

### Anti-Pattern
```sql
-- Avoid this:
ALTER TABLE order ADD COLUMN status VARCHAR(50) DEFAULT 'PENDING' NOT NULL;
```
*   **Issue**: On older PostgreSQL versions (pre-11) or with complex column definitions/expressions, this statement locks the entire table for writes while PostgreSQL rewrites all 500K rows to backfill the default value. This blocks production traffic and causes pool exhaustion.

### Mitigation: The 3-Step Rollout
```sql
-- Step 1: Add the column as nullable (fast, metadata-only lock)
ALTER TABLE order ADD COLUMN status VARCHAR(50);

-- Step 2: Backfill the default value in batches to avoid locking the table
UPDATE order SET status = 'PENDING' WHERE status IS NULL;

-- Step 3: Alter the column to enforce NOT NULL
ALTER TABLE order ALTER COLUMN status SET NOT NULL;
```
*(Note: In modern Postgres 11+, `ADD COLUMN ... DEFAULT ... NOT NULL` is optimized to be a metadata-only change, but the 3-step rollout remains the gold standard for zero-downtime database upgrades, especially when the default value is dynamic or depends on other columns).*
