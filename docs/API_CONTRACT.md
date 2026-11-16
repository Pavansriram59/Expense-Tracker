# API Contract

> **Status:** Draft  
> **Last Updated:** 2026-11-16  
> **Base URL:** `https://api.financetracker.local/v1`  
> **Auth:** Bearer JWT (Authorization header)

---

## 1. Conventions

- All request/response bodies are **JSON** (`Content-Type: application/json`).
- Timestamps are **ISO 8601** in UTC (`2026-11-16T14:30:00Z`).
- Monetary amounts are **strings** with 2 decimal places (`"125.50"`).
- Errors follow the standard envelope:

```json
{
  "detail": "Human-readable message",
  "code": "MACHINE_READABLE_CODE"
}
```

- Pagination uses `?skip=0&limit=20` query params; responses include `total`, `skip`, `limit`.

---

## 2. Authentication

### `POST /auth/register`
Register a new user.

**Request**
```json
{
  "email": "user@example.com",
  "password": "StrongP@ss1",
  "full_name": "Jane Doe"
}
```

**Response `201`**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "created_at": "2026-11-16T14:30:00Z"
}
```

---

### `POST /auth/login`
Obtain access + refresh tokens.

**Request**
```json
{
  "email": "user@example.com",
  "password": "StrongP@ss1"
}
```

**Response `200`**
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<opaque>",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

### `POST /auth/refresh`
Exchange a refresh token for a new access token.

**Request**
```json
{ "refresh_token": "<opaque>" }
```

**Response `200`** — same shape as `/auth/login`.

---

### `POST /auth/logout`
Revoke the current refresh token. 🔒 _Requires auth._

**Response `204`** — no body.

---

## 3. Transactions

### `GET /transactions` 🔒
List transactions for the authenticated user.

**Query params:** `skip`, `limit`, `type` (`income`|`expense`), `category_id`, `date_from`, `date_to`

**Response `200`**
```json
{
  "total": 150,
  "skip": 0,
  "limit": 20,
  "items": [
    {
      "id": "uuid",
      "type": "expense",
      "amount": "49.99",
      "currency": "USD",
      "category_id": "uuid",
      "date": "2026-11-15",
      "note": "Groceries",
      "created_at": "2026-11-15T18:00:00Z"
    }
  ]
}
```

---

### `POST /transactions` 🔒
Create a new transaction.

**Request**
```json
{
  "type": "expense",
  "amount": "49.99",
  "currency": "USD",
  "category_id": "uuid",
  "date": "2026-11-15",
  "note": "Groceries"
}
```

**Response `201`** — full transaction object.

---

### `GET /transactions/{id}` 🔒
Get a single transaction.

**Response `200`** — full transaction object.

---

### `PATCH /transactions/{id}` 🔒
Partially update a transaction (any writable fields).

**Response `200`** — updated transaction object.

---

### `DELETE /transactions/{id}` 🔒
Delete a transaction.

**Response `204`** — no body.

---

## 4. Categories

### `GET /categories` 🔒
List all categories (system defaults + user-created).

### `POST /categories` 🔒
Create a custom category.

### `PATCH /categories/{id}` 🔒
Update a user-owned category.

### `DELETE /categories/{id}` 🔒
Delete a user-owned category (must have no linked transactions).

---

## 5. Budgets

### `GET /budgets` 🔒
List budgets for the authenticated user.

### `POST /budgets` 🔒
Create a budget.

**Request**
```json
{
  "category_id": "uuid",
  "amount": "500.00",
  "period": "monthly",
  "start_date": "2026-11-01"
}
```

### `PATCH /budgets/{id}` 🔒
Update a budget.

### `DELETE /budgets/{id}` 🔒
Delete a budget.

---

## 6. Reports

### `GET /reports/summary` 🔒
Return total income, total expenses, and net balance for a date range.

**Query params:** `date_from`, `date_to`

### `GET /reports/by-category` 🔒
Breakdown of spending/income grouped by category.

---

## 7. HTTP Status Code Reference

| Code | Meaning                  |
|------|--------------------------|
| 200  | OK                       |
| 201  | Created                  |
| 204  | No Content               |
| 400  | Bad Request              |
| 401  | Unauthorized             |
| 403  | Forbidden                |
| 404  | Not Found                |
| 422  | Validation Error         |
| 429  | Too Many Requests        |
| 500  | Internal Server Error    |
