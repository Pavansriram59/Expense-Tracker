# System Architecture & Technical Design

> **Project:** Personal Finance Tracker  
> **Status:** Approved Architecture Blueprint  
> **Last Updated:** 2026-11-16  

---

## 1. High-Level System Overview

The system is designed as an **offline-first, multi-platform personal finance ecosystem** anchored by a central stateless **FastAPI backend**, an **Android client** acting as the primary transactional ingestion point, and a responsive **Angular web client** for desktop review and analytics.

```mermaid
flowchart TD
    subgraph Android["Android Client (Kotlin + Compose)"]
        UI_A["Compose UI (MVVM)"]
        SMS_P["SMS Ingestion Engine"]
        ROOM[("Room SQLite DB (Encrypted)")]
        SYNC_W["Sync Worker (WorkManager)"]
        UI_A <--> ROOM
        SMS_P --> ROOM
        ROOM <--> SYNC_W
    end

    subgraph Web["Web Client (Angular 18+)"]
        UI_W["Angular Standalone Components"]
        STATE_W["Signals & NgRx Store"]
        HTTP_W["HTTP Client + Auth Interceptor"]
        UI_W <--> STATE_W
        STATE_W <--> HTTP_W
    end

    subgraph Cloud["Backend Modular Monolith (FastAPI)"]
        API_GW["FastAPI REST API Gateway / Routers"]
        SVC["Domain Services (Business Logic)"]
        AUTH["Auth & Token Service"]
        SYNC_E["Delta Sync Engine"]
        ORM["SQLAlchemy ORM (Async)"]
        
        API_GW --> AUTH
        API_GW --> SVC
        API_GW --> SYNC_E
        SVC --> ORM
        SYNC_E --> ORM
    end

    subgraph Data["Database Infrastructure"]
        PG[("PostgreSQL 16")]
        ORM <--> PG
    end

    SYNC_W -- "HTTPS / Delta Sync (JWT)" --> API_GW
    HTTP_W -- "HTTPS / REST (JWT)" --> API_GW
```

---

## 2. Android Client Architecture

The Android application strictly implements **MVVM with Clean Architecture** and treats the local Room database as the immutable **Single Source of Truth (SSOT)**.

```mermaid
flowchart LR
    subgraph Presentation["Presentation Layer (Jetpack Compose)"]
        Screens["Compose Screens / NavHost"]
        VMs["ViewModels (StateFlow / UI State)"]
        Screens <--> VMs
    end

    subgraph Domain["Domain Layer (Pure Kotlin)"]
        UseCases["Use Cases / Interactors"]
        DomainModels["Domain Entities"]
        RepoInterfaces["Repository Interfaces"]
        VMs --> UseCases
        UseCases --> RepoInterfaces
        UseCases -.-> DomainModels
    end

    subgraph Data["Data Layer (Android & Room)"]
        RepoImpl["Repository Implementations"]
        LocalDS["Local Data Source (Room DAOs)"]
        RemoteDS["Remote Data Source (Retrofit)"]
        RoomDB[("Room Database (SQLCipher)")]
        API["Backend REST API"]
        
        RepoInterfaces <|-- RepoImpl
        RepoImpl <--> LocalDS
        RepoImpl <--> RemoteDS
        LocalDS <--> RoomDB
        RemoteDS <--> API
    end
```

### 2.1 Android Package Structure
```
android/app/src/main/java/com/financetracker/
├── core/
│   ├── common/             # Result wrappers, Dispatchers, Extensions, Constants
│   ├── database/           # Room DB instance, Entities, DAOs, TypeConverters
│   ├── datastore/          # EncryptedSharedPreferences / DataStore for tokens & prefs
│   ├── network/            # Retrofit instances, AuthInterceptor, NetworkBoundResource
│   ├── model/              # Shared domain models (Money, Currency, CategoryType)
│   └── sms/                # SMS parsing engine, bank regexes, deduplicator
├── di/                     # Hilt Dependency Injection modules
├── domain/
│   ├── usecase/
│   │   ├── transaction/    # GetTransactions, SaveTransaction, SplitTransaction
│   │   ├── split/          # CalculateSplitShares, SettleDebt
│   │   ├── account/        # ReconcileAccountBalance, TransferFunds
│   │   ├── budget/         # EvaluateBudgetStatus
│   │   └── sync/           # PerformDeltaSyncUseCase
│   └── repository/         # Repository contracts
├── data/
│   ├── repository/         # TransactionRepositoryImpl, AccountRepositoryImpl, etc.
│   └── sync/               # SyncManager, SyncWorker, SyncConflictResolver
└── presentation/
    ├── navigation/         # NavGraph, Destinations, BottomBar
    ├── theme/              # Material 3 Color Schemes, Typography, Shapes
    ├── components/         # Reusable Compose widgets (CurrencyText, CategoryIcon, FilterChip)
    ├── dashboard/          # DashboardScreen, DashboardViewModel
    ├── transactions/       # TransactionListScreen, TransactionDetailScreen, AddEditScreen
    ├── split/              # SplitExpenseScreen, FriendsListScreen, SettlementScreen
    ├── accounts/           # AccountListScreen, AccountDetailScreen
    ├── budgets/            # BudgetOverviewScreen, AddBudgetDialog
    ├── review/             # PendingSmsReviewScreen, SmsDetailReviewDialog
    └── analytics/          # SpendingChartsScreen, CategoryDrillDownScreen
```

### 2.2 SMS Ingestion Subsystem (On-Device)
The SMS subsystem operates autonomously without requiring backend network availability:

```mermaid
flowchart TD
    SMS["Incoming SMS Broadcast"] --> REC["SmsBroadcastReceiver"]
    REC --> FILTER{"Financial Sender Filter\n(e.g., AD-HDFCBK, VM-ICICIB)"}
    FILTER -- "Not Bank SMS" --> DISCARD["Discard Immediately"]
    FILTER -- "Financial SMS" --> PARSER["Bank Regex & Pattern Engine"]
    
    PARSER --> EXTRACT["Extract: Amount, Merchant/VPA,\nType (Debit/Credit), Last 4 digits, Date, Ref"]
    EXTRACT --> DEDUP{"Deduplication Check\n(Hash in local sms_inbox_logs)"}
    DEDUP -- "Duplicate" --> DISCARD
    DEDUP -- "New Transaction" --> INSERT["Insert into Room with status:\nPENDING_REVIEW"]
    
    INSERT --> NOTIF["Post System Notification\n'Spent ₹450 at Swiggy. Confirm or Split?'"]
    NOTIF --> USER_REV["User Review Screen in Compose"]
    USER_REV --> CONFIRM{"User Action"}
    CONFIRM -- "Confirm" --> COMMIT["Update status: CONFIRMED\nDebit Account Balance"]
    CONFIRM -- "Split" --> SPLIT["Open Split Flow\nCalculate Friend Receivables"]
    CONFIRM -- "Ignore" --> IGNORE["Update status: IGNORED"]
```

---

## 3. Backend Architecture (FastAPI Modular Monolith)

The backend follows a **Stateless Modular Monolith** pattern. Routers remain thin, delegating all domain logic and invariants to the service layer.

### 3.1 Backend Module Hierarchy
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── router.py           # Master v1 router aggregating feature endpoints
│   │   │   ├── auth.py             # Login, register, refresh, logout
│   │   │   ├── accounts.py         # Account CRUD, balance adjustments
│   │   │   ├── transactions.py     # Transaction CRUD, transfers
│   │   │   ├── splits.py           # Split bills, friends, settlements
│   │   │   ├── categories.py       # Default and custom categories
│   │   │   ├── budgets.py          # Category budgets, threshold checks
│   │   │   ├── goals.py            # Savings goals, progress contributions
│   │   │   ├── recurring.py        # Subscription and bill recurrence rules
│   │   │   ├── analytics.py        # Dashboard rollups, category breakdowns, trends
│   │   │   └── sync.py             # Delta sync: /push and /pull
│   │   └── deps.py                 # Dependency injection: get_current_user, get_db
│   ├── core/
│   │   ├── config.py               # Pydantic BaseSettings (env vars)
│   │   ├── security.py             # Password hashing (Argon2id/bcrypt), JWT encode/decode
│   │   ├── exceptions.py           # Domain exceptions & RFC 7807 problem handlers
│   │   └── logging.py              # Structured JSON logging (zero PII)
│   ├── models/                     # SQLAlchemy 2.0 async ORM models
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   ├── split.py
│   │   ├── budget.py
│   │   ├── goal.py
│   │   ├── recurring.py
│   │   └── sync_audit.py
│   ├── schemas/                    # Pydantic v2 validation models
│   │   ├── auth.py
│   │   ├── account.py
│   │   ├── transaction.py
│   │   ├── split.py
│   │   ├── budget.py
│   │   ├── analytics.py
│   │   └── sync.py
│   ├── services/                   # Encapsulated Business Logic (Strictly No DB calls in Routers)
│   │   ├── auth_service.py
│   │   ├── account_service.py
│   │   ├── transaction_service.py
│   │   ├── split_service.py
│   │   ├── budget_service.py
│   │   ├── analytics_service.py
│   │   └── sync_service.py
│   ├── db/
│   │   ├── session.py              # Async engine and sessionmaker
│   │   └── base.py                 # Base declarative model
│   └── main.py                     # App factory, CORS, exception handlers, telemetry
├── alembic/                        # Database migration scripts
├── tests/
│   ├── unit/                       # Business logic unit tests
│   └── integration/                # Full API async tests with test PostgreSQL
├── Dockerfile
└── docker-compose.yml
```

---

## 4. Web Application Architecture (Angular 18+)

The Web application is structured for desktop and tablet users who require large-screen financial reports, data export, and manual transaction review:
- **Standalone Components:** No `NgModule` boilerplate; lazy-loaded feature routes.
- **Signals + RxJS:** Angular Signals for local component reactivity; RxJS for complex asynchronous streams and HTTP pipelines.
- **NgRx Store / SignalStore:** Centralized state management for accounts, active filters, and cached financial summaries.
- **Styling & UI:** Tailwind CSS for layout utility; Spartan UI / Angular Material for accessible UI primitives; Apache ECharts for rendering smooth time-series graphs and categorical sunburst/donut charts.
- **HTTP Interceptor:** Transparent JWT bearer attachment, proactive token refresh upon receiving 401 Unauthorized, and graceful redirect to login.

---

## 5. Offline-First & Bidirectional Synchronization Strategy

To guarantee continuous usability without internet connectivity, the system uses a **Timestamped Delta Synchronization Engine** with client-side UUIDv7 generation.

```mermaid
sequenceDiagram
    autonumber
    participant Client as Android Client (Room)
    participant Worker as WorkManager (SyncWorker)
    participant Server as FastAPI (/sync/push & /pull)
    participant DB as PostgreSQL 16

    Note over Client: User creates/edits transactions offline.<br/>Saved in Room with sync_status = 'PENDING'
    Note over Worker: Connectivity restored or periodic trigger
    Worker->>Client: Query entities where sync_status != 'SYNCED'
    Worker->>Server: POST /v1/sync/push { mutations: [ ... ], client_time: T1 }
    
    activate Server
    Server->>DB: Begin Transaction
    loop For each mutation in batch
        Server->>DB: Verify UUID and compare client_updated_at with server_updated_at
        alt No Conflict
            Server->>DB: Apply INSERT / UPDATE / Tombstone Soft Delete
        else Server version is newer (Conflict)
            Server->>DB: Execute Conflict Rule (Last-Write-Wins or append)
        end
    end
    Server->>DB: Commit Transaction & update sync audit log
    Server-->>Worker: 200 OK { accepted_ids: [...], rejected_ids: [...], server_time: T2 }
    deactivate Server

    Worker->>Client: Mark accepted entities as sync_status = 'SYNCED'
    
    Worker->>Server: GET /v1/sync/pull?since={last_sync_timestamp}
    Server->>DB: Fetch records where server_updated_at > last_sync_timestamp
    Server-->>Worker: 200 OK { changes: [ ... ], new_sync_timestamp: T3 }
    Worker->>Client: Upsert server changes into Room DB
    Worker->>Client: Save new_sync_timestamp locally
```

### 5.1 UUIDv7 Primary Keys
All entities use **UUIDv7** (time-ordered UUIDs) generated on the client. This guarantees:
- Zero ID collisions between offline Android records and server records.
- Sequential B-tree indexing in PostgreSQL and SQLite, preventing database page fragmentation.

### 5.2 Conflict Resolution Invariants
1. **LWW (Last-Write-Wins):** For standard entities (Account name, Category color, Transaction note), the record with the most recent `updated_at` timestamp takes precedence.
2. **Immutable Financial Events for Splits:** Split settlements and debt payments are recorded as immutable transaction logs rather than mutable balance overrides. Adding a settlement appends a row to `settlements`, ensuring concurrent updates from different devices never overwrite each other.
3. **Soft Deletion & Tombstones:** Deleted entities set `is_deleted = TRUE` and retain `updated_at = now()`. A dedicated `sync_tombstones` table guarantees that devices that have been offline for weeks still receive deletion updates.

---

## 6. End-to-End Data Flow Scenarios

### 6.1 Scenario 1: Expense Splitting Financial Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Android as Android App
    actor Friend as Rahul (Friend)
    participant Server as Backend API
    participant DB as PostgreSQL

    User->>Android: Pays ₹2,000 for dinner at restaurant
    Android->>Android: Transaction Created: Amount = ₹2,000 (Gross Debit from HDFC Bank)
    User->>Android: Selects "Split Equally with Rahul"
    Android->>Android: Compute: Personal Expense = ₹1,000<br/>Rahul Owed = ₹1,000 (Accounts Receivable)
    Android->>Android: Update Transaction: personal_amount = 1000.00, is_split = true
    Android->>Android: Insert split_bill (total: 2000.00) & split_bill_member (Rahul, owed: 1000.00)
    
    Note over Android: Syncs with backend
    Android->>Server: Push Transaction & Split records
    Server->>DB: Commit Transaction & Split Ledger
    
    Note over User,Friend: Next day, Rahul transfers ₹1,000 to User via UPI
    User->>Android: Record Settlement: Received ₹1,000 from Rahul into HDFC Bank
    Android->>Android: Insert settlement: friend_id = Rahul, amount = 1000.00, account_id = HDFC
    Android->>Android: HDFC Account Balance increases by ₹1,000
    Android->>Android: Rahul's debt reduced to ₹0
    Note over Android: Critical: Net Income for User remains ₹0 (Not counted as income)
```

---

## 7. Security, Privacy & Integrity Architecture

| Security Domain | Architectural Implementation |
|---|---|
| **Data at Rest (Android)** | Local Room DB encrypted via **256-bit SQLCipher**. Passphrase derived securely from the Android Keystore. |
| **Data in Transit** | **TLS 1.3** required on all endpoints. Android network security configuration enforces strict domain certificates. |
| **Authentication** | **JWT with Refresh Token Family Rotation**: Short-lived access token (15 mins) and cryptographically random, hashed refresh token (7 days). If a compromised refresh token is reused, the entire token family is immediately revoked. |
| **SMS Data Sovereignty** | **Zero raw SMS leaves the device.** Regex extraction occurs exclusively in the Android process space. SMS strings are zeroed out in memory after parsing. |
| **Monetary Precision** | All monetary amounts stored as `NUMERIC(14, 2)` in PostgreSQL and mapped to `BigDecimal` in Kotlin / `Decimal` in Python. Floating-point types are strictly forbidden. |
| **PII & Log Sanitization** | Structured loggers filter and mask email addresses, names, card numbers, and tokens. |

---

## 8. Deployment & DevOps Architecture

### 8.1 Local & Development Topology
```yaml
# docker-compose.yml structure
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: financetracker
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/financetracker
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db

  web:
    build: ./web
    ports:
      - "4200:80"
```

### 8.2 Production Deployment Path
- **Backend:** Containerized FastAPI app served via Uvicorn behind an Nginx reverse proxy providing automated Let's Encrypt SSL termination.
- **Database:** Managed PostgreSQL instance with automated daily snapshots and write-ahead log (WAL) archiving.
- **Android CI/CD:** GitHub Actions workflow running `./gradlew test` (unit tests), `ktlintCheck`, and producing unsigned APKs / release AABs.
- **Backend CI/CD:** GitHub Actions workflow running `ruff` linting, `mypy` type validation, and `pytest` with a live PostgreSQL service container.
