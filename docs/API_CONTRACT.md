# REST API Contract & Specification

> **Project:** Personal Finance Tracker  
> **Status:** Approved Architecture Blueprint  
> **Last Updated:** 2026-11-16  
> **Base URL:** `https://api.financetracker.local/v1`  
> **Format:** JSON (`application/json`)  
> **Auth:** Bearer JWT in `Authorization` header

---

## 1. Global Conventions & Protocols

### 1.1 Headers
| Header | Required | Description |
|---|---|---|
| `Authorization` | Yes (for protected endpoints) | `Bearer <access_token>` |
| `Content-Type` | Yes (for POST/PATCH) | `application/json` |
| `X-Request-ID` | Recommended | Client-generated UUID for distributed request tracing |
| `X-Client-Version` | Recommended | e.g. `android-1.0.0` or `web-1.0.0` |

### 1.2 Data Formatting Standards
- **Identifiers:** Standard lowercase UUIDv7 strings (e.g. `"018d42b1-6a9c-7000-8000-000000000001"`).
- **Monetary Values:** Fixed-point strings with exactly 2 decimal places (e.g. `"1499.50"`). Never floating-point numbers.
- **Timestamps:** ISO 8601 formatted in UTC with trailing `Z` (e.g. `"2026-11-16T14:30:00Z"`).
- **Dates:** ISO 8601 calendar date (e.g. `"2026-11-16"`).

### 1.3 Standard Error Envelope (RFC 7807 Inspired)
All 4xx and 5xx responses conform strictly to this structure:
```json
{
  "code": "RESOURCE_NOT_FOUND",
  "detail": "Transaction with id 018d42b1-6a9c-7000-8000-000000000001 was not found.",
  "errors": [
    {
      "field": "transaction_id",
      "message": "Invalid UUID format or resource does not exist"
    }
  ],
  "request_id": "c56a4180-65aa-42ec-a945-5fd21dec0538"
}
```

---

## 2. Authentication & Profile Endpoints

### `POST /auth/register`
Create a new user account.

**Request**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "Sriram Kumar",
  "base_currency": "INR"
}
```
**Response `201 Created`**
```json
{
  "id": "018d42b1-6a9c-7000-8000-000000000001",
  "email": "user@example.com",
  "full_name": "Sriram Kumar",
  "base_currency": "INR",
  "created_at": "2026-11-16T14:30:00Z"
}
```

---

### `POST /auth/login`
Authenticate with credentials and obtain an access token + rotating refresh token.

**Request**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
**Response `200 OK`**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "7b8e1a90c42f4837a4d59182...",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

### `POST /auth/refresh`
Exchange an active refresh token for a fresh access token and a new rotated refresh token.

**Request**
```json
{
  "refresh_token": "7b8e1a90c42f4837a4d59182..."
}
```
**Response `200 OK`** (Returns new pair, invalidating the old refresh token)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "9a3f2d81e01c4516b2e17734...",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

### `POST /auth/logout` 🔒
Revoke current refresh token family.

**Response `204 No Content`**

---

### `GET /users/me` 🔒
Retrieve profile and preferences of the authenticated user.

**Response `200 OK`**
```json
{
  "id": "018d42b1-6a9c-7000-8000-000000000001",
  "email": "user@example.com",
  "full_name": "Sriram Kumar",
  "base_currency": "INR",
  "created_at": "2026-11-16T14:30:00Z"
}
```

---

## 3. Account Endpoints

### `GET /accounts` 🔒
List all active financial accounts for the authenticated user.

**Response `200 OK`**
```json
[
  {
    "id": "018d42b1-7b00-7000-8000-000000000002",
    "name": "HDFC Salary Account",
    "account_type": "BANK",
    "institution_name": "HDFC Bank",
    "account_number_suffix": "4912",
    "currency": "INR",
    "current_balance": "45250.75",
    "credit_limit": null,
    "billing_cycle_day": null,
    "payment_due_day": null,
    "color_hex": "#2563EB",
    "icon_name": "account_balance",
    "is_archived": false,
    "updated_at": "2026-11-16T14:30:00Z"
  },
  {
    "id": "018d42b1-7b00-7000-8000-000000000003",
    "name": "Amazon Pay ICICI Card",
    "account_type": "CREDIT_CARD",
    "institution_name": "ICICI Bank",
    "account_number_suffix": "8821",
    "currency": "INR",
    "current_balance": "-12400.00",
    "credit_limit": "200000.00",
    "billing_cycle_day": 12,
    "payment_due_day": 2,
    "color_hex": "#DC2626",
    "icon_name": "credit_card",
    "is_archived": false,
    "updated_at": "2026-11-16T14:30:00Z"
  }
]
```

---

### `POST /accounts` 🔒
Create a new financial account. Client supplies UUIDv7.

**Request**
```json
{
  "id": "018d42b1-7b00-7000-8000-000000000004",
  "name": "Cash Wallet",
  "account_type": "CASH",
  "currency": "INR",
  "initial_balance": "3500.00",
  "color_hex": "#10B981",
  "icon_name": "payments"
}
```
**Response `201 Created`**

---

### `POST /accounts/transfer` 🔒
Atomically transfer funds between two accounts. Creates a single `TRANSFER` transaction that updates both balances.

**Request**
```json
{
  "id": "018d42b1-7b00-7000-8000-000000000005",
  "from_account_id": "018d42b1-7b00-7000-8000-000000000002",
  "to_account_id": "018d42b1-7b00-7000-8000-000000000004",
  "amount": "2000.00",
  "transaction_date": "2026-11-16T15:00:00Z",
  "note": "ATM Cash Withdrawal"
}
```
**Response `201 Created`**

---

## 4. Category Endpoints

### `GET /categories` 🔒
Fetch all system-default and user-custom categories.

**Response `200 OK`**
```json
[
  {
    "id": "018d42b1-8c00-7000-8000-000000000010",
    "name": "Food & Dining",
    "parent_id": null,
    "category_type": "EXPENSE",
    "icon_name": "restaurant",
    "color_hex": "#F97316",
    "is_system": true,
    "subcategories": [
      {
        "id": "018d42b1-8c00-7000-8000-000000000011",
        "name": "Restaurants",
        "parent_id": "018d42b1-8c00-7000-8000-000000000010",
        "category_type": "EXPENSE",
        "icon_name": "dining",
        "color_hex": "#F97316",
        "is_system": true
      }
    ]
  }
]
```

---

## 5. Transaction Endpoints

### `GET /transactions` 🔒
Query transactions with rich filtering and pagination.

**Query Parameters:**
- `account_id` (UUID, optional)
- `category_id` (UUID, optional)
- `type` (`EXPENSE`, `INCOME`, `TRANSFER`, optional)
- `status` (`CONFIRMED`, `PENDING_REVIEW`, optional)
- `is_split` (boolean, optional)
- `date_from` (ISO date, optional)
- `date_to` (ISO date, optional)
- `search` (string, optional: matches merchant or note)
- `skip` (integer, default `0`)
- `limit` (integer, default `20`, max `100`)

**Response `200 OK`**
```json
{
  "total": 342,
  "skip": 0,
  "limit": 20,
  "items": [
    {
      "id": "018d42b1-9d00-7000-8000-000000000020",
      "account_id": "018d42b1-7b00-7000-8000-000000000002",
      "to_account_id": null,
      "category_id": "018d42b1-8c00-7000-8000-000000000011",
      "transaction_type": "EXPENSE",
      "amount": "2000.00",
      "personal_amount": "500.00",
      "currency": "INR",
      "transaction_date": "2026-11-16T19:30:00Z",
      "status": "CONFIRMED",
      "merchant_name": "Toscano Restaurant",
      "is_split": true,
      "note": "Team dinner",
      "tags": ["dining", "friends"],
      "reference_number": "UPI/1234567890",
      "source_sms_hash": "a1b2c3d4...",
      "created_at": "2026-11-16T19:35:00Z",
      "updated_at": "2026-11-16T19:40:00Z"
    }
  ]
}
```

---

### `POST /transactions` 🔒
Record a new confirmed or draft transaction. Client supplies UUIDv7.

**Request**
```json
{
  "id": "018d42b1-9d00-7000-8000-000000000021",
  "account_id": "018d42b1-7b00-7000-8000-000000000002",
  "category_id": "018d42b1-8c00-7000-8000-000000000011",
  "transaction_type": "EXPENSE",
  "amount": "450.00",
  "personal_amount": "450.00",
  "currency": "INR",
  "transaction_date": "2026-11-16T12:15:00Z",
  "status": "CONFIRMED",
  "merchant_name": "Starbucks Coffee",
  "is_split": false,
  "note": "Morning cappuccino"
}
```
**Response `201 Created`**

---

### `PATCH /transactions/{id}` 🔒
Partially update transaction properties (e.g. adjust category or notes).

**Response `200 OK`**

---

### `DELETE /transactions/{id}` 🔒
Soft-delete transaction (marks `is_deleted = true`). Reverts account balance.

**Response `204 No Content`**

---

## 6. Split Expenses & Friends Endpoints

### `GET /friends` 🔒
List all friends and their net balance owed to or by the user.

**Response `200 OK`**
```json
[
  {
    "id": "018d42b1-ae00-7000-8000-000000000030",
    "name": "Rahul Sharma",
    "phone_number": "+919876543210",
    "email": "rahul@example.com",
    "net_balance": "1500.00",
    "is_active": true
  }
]
```
*(Note: positive `net_balance` means friend owes user; negative means user owes friend)*

---

### `POST /splits` 🔒
Create an expense split allocation linked to an existing transaction.

**Request**
```json
{
  "id": "018d42b1-bf00-7000-8000-000000000040",
  "transaction_id": "018d42b1-9d00-7000-8000-000000000020",
  "split_strategy": "EQUAL",
  "user_share_amount": "500.00",
  "members": [
    {
      "id": "018d42b1-bf00-7000-8000-000000000041",
      "friend_id": "018d42b1-ae00-7000-8000-000000000030",
      "owed_amount": "500.00"
    },
    {
      "id": "018d42b1-bf00-7000-8000-000000000042",
      "friend_id": "018d42b1-ae00-7000-8000-000000000031",
      "owed_amount": "1000.00"
    }
  ],
  "notes": "Dinner split"
}
```
**Response `201 Created`**

---

### `POST /settlements` 🔒
Record a debt settlement between the user and a friend.

**Request**
```json
{
  "id": "018d42b1-cf00-7000-8000-000000000050",
  "friend_id": "018d42b1-ae00-7000-8000-000000000030",
  "account_id": "018d42b1-7b00-7000-8000-000000000002",
  "amount": "500.00",
  "settlement_type": "RECEIVED_FROM_FRIEND",
  "settlement_date": "2026-11-17T10:00:00Z",
  "notes": "GPay settlement for Toscano dinner"
}
```
**Response `201 Created`**

---

## 7. Budgets & Goals Endpoints

### `GET /budgets` 🔒
Retrieve active category budgets and calculated real-time spending progress.

**Response `200 OK`**
```json
[
  {
    "id": "018d42b1-df00-7000-8000-000000000060",
    "category_id": "018d42b1-8c00-7000-8000-000000000010",
    "category_name": "Food & Dining",
    "amount": "15000.00",
    "period": "MONTHLY",
    "spent_amount": "9250.00",
    "remaining_amount": "5750.00",
    "percentage_used": 61.67,
    "alert_threshold_percent": 80,
    "is_alert_triggered": false
  }
]
```

---

### `GET /goals` 🔒
List all active savings goals and current progression.

**Response `200 OK`**
```json
[
  {
    "id": "018d42b1-ef00-7000-8000-000000000070",
    "name": "Japan Vacation Fund",
    "target_amount": "150000.00",
    "current_amount": "45000.00",
    "progress_percent": 30.00,
    "target_date": "2027-04-01",
    "status": "ACTIVE"
  }
]
```

---

## 8. Analytics & Dashboard Endpoints

### `GET /analytics/dashboard` 🔒
Consolidated payload powering the primary app dashboard.

**Query Parameters:**
- `month` (e.g. `2026-11`)

**Response `200 OK`**
```json
{
  "summary": {
    "net_worth": "235800.00",
    "total_liquid_cash": "185800.00",
    "total_credit_debt": "12400.00",
    "total_money_owed_by_friends": "4500.00",
    "total_money_owed_to_friends": "0.00"
  },
  "current_month": {
    "total_income": "120000.00",
    "total_gross_expense": "48500.00",
    "total_personal_expense": "42500.00",
    "net_savings": "77500.00",
    "savings_rate_percent": 64.58
  },
  "category_breakdown": [
    {
      "category_id": "018d42b1-8c00-7000-8000-000000000010",
      "category_name": "Food & Dining",
      "spent_amount": "12400.00",
      "percentage_of_total": 29.17
    }
  ],
  "recent_transactions": [ ... ]
}
```

---

## 9. Offline Delta Synchronization Endpoints

### `POST /sync/push` 🔒
Batch upload offline mutations (creates, updates, deletes) recorded on client.

**Request**
```json
{
  "client_sync_time": "2026-11-16T20:00:00Z",
  "mutations": {
    "accounts": [ ... ],
    "categories": [ ... ],
    "transactions": [
      {
        "id": "018d42b1-9d00-7000-8000-000000000021",
        "account_id": "018d42b1-7b00-7000-8000-000000000002",
        "amount": "450.00",
        "personal_amount": "450.00",
        "transaction_date": "2026-11-16T12:15:00Z",
        "status": "CONFIRMED",
        "updated_at": "2026-11-16T12:15:00Z",
        "is_deleted": false
      }
    ],
    "splits": [ ... ],
    "settlements": [ ... ]
  }
}
```
**Response `200 OK`**
```json
{
  "status": "SUCCESS",
  "accepted_ids": ["018d42b1-9d00-7000-8000-000000000021"],
  "conflicts": [],
  "server_sync_time": "2026-11-16T20:01:05Z"
}
```

---

### `GET /sync/pull` 🔒
Download remote changes modified since the high-watermark timestamp.

**Query Parameters:**
- `since`: ISO 8601 UTC timestamp (e.g. `2026-11-16T18:00:00Z`)

**Response `200 OK`**
```json
{
  "server_sync_time": "2026-11-16T20:01:10Z",
  "changes": {
    "accounts": [ ... ],
    "categories": [ ... ],
    "transactions": [ ... ],
    "splits": [ ... ],
    "settlements": [ ... ],
    "tombstones": [
      {
        "entity_type": "transactions",
        "entity_id": "018d42b1-9d00-7000-8000-000000000099",
        "deleted_at": "2026-11-16T19:55:00Z"
      }
    ]
  }
}
```
