# Database Schema

> **Status:** Draft  
> **Last Updated:** 2026-11-16  
> **Database:** PostgreSQL 16

---

## 1. Entity Relationship Diagram (Textual)

```
users ──< transactions >── categories
  │
  └──< budgets >── categories
```

---

## 2. Tables

### 2.1 `users`

| Column         | Type                    | Constraints                  |
|----------------|-------------------------|------------------------------|
| id             | UUID                    | PRIMARY KEY, default gen     |
| email          | VARCHAR(255)            | UNIQUE, NOT NULL             |
| hashed_password| VARCHAR(255)            | NOT NULL                     |
| full_name      | VARCHAR(255)            |                              |
| currency       | CHAR(3)                 | DEFAULT 'USD'                |
| is_active      | BOOLEAN                 | DEFAULT TRUE                 |
| created_at     | TIMESTAMPTZ             | DEFAULT now()                |
| updated_at     | TIMESTAMPTZ             | DEFAULT now()                |

---

### 2.2 `categories`

| Column      | Type         | Constraints                              |
|-------------|--------------|------------------------------------------|
| id          | UUID         | PRIMARY KEY                              |
| user_id     | UUID         | FK → users.id, NULL = system default     |
| name        | VARCHAR(100) | NOT NULL                                 |
| type        | VARCHAR(10)  | CHECK IN ('income', 'expense')           |
| color_hex   | CHAR(7)      | e.g. `#FF5733`                           |
| icon        | VARCHAR(50)  |                                          |
| created_at  | TIMESTAMPTZ  | DEFAULT now()                            |

---

### 2.3 `transactions`

| Column       | Type          | Constraints                        |
|--------------|---------------|------------------------------------|
| id           | UUID          | PRIMARY KEY                        |
| user_id      | UUID          | FK → users.id, NOT NULL            |
| category_id  | UUID          | FK → categories.id                 |
| type         | VARCHAR(10)   | CHECK IN ('income', 'expense')     |
| amount       | NUMERIC(12,2) | NOT NULL, > 0                      |
| currency     | CHAR(3)       | DEFAULT 'USD'                      |
| date         | DATE          | NOT NULL                           |
| note         | TEXT          |                                    |
| receipt_url  | TEXT          |                                    |
| created_at   | TIMESTAMPTZ   | DEFAULT now()                      |
| updated_at   | TIMESTAMPTZ   | DEFAULT now()                      |

---

### 2.4 `budgets`

| Column      | Type          | Constraints                        |
|-------------|---------------|------------------------------------|
| id          | UUID          | PRIMARY KEY                        |
| user_id     | UUID          | FK → users.id, NOT NULL            |
| category_id | UUID          | FK → categories.id, NOT NULL       |
| amount      | NUMERIC(12,2) | NOT NULL, > 0                      |
| period      | VARCHAR(10)   | CHECK IN ('monthly', 'weekly')     |
| start_date  | DATE          | NOT NULL                           |
| end_date    | DATE          |                                    |
| created_at  | TIMESTAMPTZ   | DEFAULT now()                      |

---

### 2.5 `refresh_tokens`

| Column      | Type        | Constraints              |
|-------------|-------------|--------------------------|
| id          | UUID        | PRIMARY KEY              |
| user_id     | UUID        | FK → users.id, NOT NULL  |
| token_hash  | VARCHAR(64) | UNIQUE, NOT NULL         |
| expires_at  | TIMESTAMPTZ | NOT NULL                 |
| revoked     | BOOLEAN     | DEFAULT FALSE            |
| created_at  | TIMESTAMPTZ | DEFAULT now()            |

---

## 3. Indexes

```sql
-- Fast lookup of transactions per user
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_date    ON transactions(user_id, date DESC);

-- Budget lookups
CREATE INDEX idx_budgets_user_id ON budgets(user_id);

-- Token validation
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);
```

---

## 4. Migration Strategy

- Managed by **Alembic** (auto-generated revisions).
- Each PR that touches schema must include a corresponding migration file.
- Never delete columns in production — deprecate first, remove in a later migration.
