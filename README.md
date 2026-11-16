# 💰 Personal Finance Tracker (Axio-Inspired)

> An offline-first, privacy-focused personal finance management system designed to track income, expenses, bank accounts, credit cards, and UPI transactions. Featuring automated on-device bank SMS transaction detection, non-distorting split expense management, budgets, savings goals, and cross-platform synchronization between Android, FastAPI backend, and Angular web.

---

## ✨ Core Features & Highlights

- 📱 **Automated On-Device SMS Transaction Ingestion (Android):**
  - Instant detection of incoming bank, UPI, and credit card debit/credit SMS messages.
  - On-device regex and heuristic parsing engine (zero raw SMS data uploaded to the cloud).
  - Smart deduplication and "Pending Review" confirmation queue with actionable push notifications.
  - Policy-compliant modular ingestion architecture with fallback to notification listeners or synthetic test fixtures.
- 👥 **Fair Split Expenses & Friends Ledger:**
  - Real-world expense splitting (Equal, Exact, Percentage, Shares).
  - **Financial Integrity Guarantee:** Preserves the gross bank account debit while isolating net personal expense. Money owed by friends is tracked as receivables (`ACCOUNTS_RECEIVABLE`) and friend repayments are never misclassified as income.
  - Partial and full settlement tracking with complete audit trail.
- 💳 **Unified Multi-Account Management:**
  - Track liquid Bank Accounts, Credit Cards (with limits, billing cycles, and due dates), Cash, and UPI Wallets.
  - Account-to-account transfers (e.g., ATM withdrawals or credit card bill payments) that do not distort income or expenses.
- 📊 **Budgets & Analytics:**
  - Category-based monthly spending limits with proactive 80% and 100% threshold alerts.
  - Real-time Net Worth calculation (Liquid Assets minus Credit Card liabilities).
  - Cash flow velocity, burn rate, and category breakdowns rendered via Jetpack Compose and Apache ECharts.
- 🎯 **Savings Goals & Recurring Bills:**
  - Target amount, deadline, and contribution tracking for savings goals.
  - Recurring bill and subscription reminders with native Android alarms.
- 🔄 **Offline-First Delta Synchronization:**
  - 100% functional offline on Android using local encrypted Room database as the Single Source of Truth.
  - Seamless two-way delta sync (`/v1/sync/push` & `/v1/sync/pull`) using client-generated UUIDv7 keys and soft-delete tombstones.

---

## 🏗️ Technology Stack

| Layer | Platform | Technologies | Key Responsibilities |
|---|---|---|---|
| **Android Client** | Native Android (API 28+) | Kotlin, Jetpack Compose, MVVM + Clean Architecture, Room (SQLCipher), Hilt, Coroutines, StateFlow, WorkManager | On-device SMS parsing, offline-first transaction entry, local encrypted storage, delta sync worker |
| **Backend API** | Python 3.12+ | FastAPI, SQLAlchemy 2.0 (Async), Alembic, Pydantic v2, Pytest, Uvicorn | Stateless modular monolith, JWT token family rotation, delta sync engine, financial domain rules |
| **Database** | Relational | PostgreSQL 16 (Server), SQLite 3.35+ / Room (Client) | Multi-tenant financial ledger, `NUMERIC(14,2)` precision, time-ordered UUIDv7 indexing |
| **Web Client** | Modern Web | Angular 18+, TypeScript, Tailwind CSS, Angular Signals, RxJS, Apache ECharts | Desktop/tablet dashboard, financial reporting, data export, responsive management |
| **Infrastructure** | Containerization & CI | Docker, Docker Compose, GitHub Actions | Reproducible development environment, automated linting (`ruff`, `ktlint`), automated test suites |

---

## 📁 Repository Structure

```
Expense Tracker/                          ← Monorepo root
├── android/                              ← Native Android application (Kotlin + Jetpack Compose)
│   └── app/src/main/java/com/financetracker/
│       ├── core/                         # Database, network, SMS parser, common models
│       ├── di/                           # Hilt dependency injection modules
│       ├── domain/                       # Use cases, repository interfaces, domain rules
│       ├── data/                         # Room DAOs, repository implementations, sync worker
│       └── presentation/                 # Compose screens, ViewModels, navigation, theme
├── backend/                              ← Python / FastAPI REST API
│   ├── app/
│   │   ├── api/v1/                       # Thin route handlers (auth, accounts, transactions, sync)
│   │   ├── core/                         # Config, security (Argon2id/JWT), exception handlers
│   │   ├── models/                       # SQLAlchemy 2.0 declarative ORM models
│   │   ├── schemas/                      # Pydantic v2 validation models
│   │   ├── services/                     # Business logic and domain calculations
│   │   ├── db/                           # Async database session & engine
│   │   └── main.py                       # Application entry point & middleware
│   ├── alembic/                          # Database schema migrations
│   ├── tests/                            # Unit & live PostgreSQL integration tests
│   └── Dockerfile
├── web/                                  ← Angular web application
│   └── src/app/
│       ├── core/                         # Auth guards, HTTP interceptors, singleton services
│       ├── shared/                       # Reusable UI components, pipes, directives
│       └── features/                     # Feature slices (dashboard, transactions, reports)
├── docs/                                 ← Master Technical Blueprint
│   ├── REQUIREMENTS.md                   ← Functional & non-functional requirements
│   ├── ARCHITECTURE.md                   ← System architecture, data flows, and diagrams
│   ├── DATABASE_SCHEMA.md                ← Database entities, constraints, indexes & ERD
│   └── API_CONTRACT.md                   ← REST API endpoint contracts & payloads
├── AGENTS.md                             ← Guidelines & rules for AI coding assistants
├── DEVELOPMENT_LOG.md                    ← Phased milestones, changelog, and decisions
├── docker-compose.yml                    ← Local multi-container orchestration
└── README.md                             ← You are here
```

---

## 🗺️ Phased Development Roadmap

- [x] **Milestone 0: Architecture & Repository Blueprint** (Complete system specs, schemas, contracts, guidelines).
- [ ] **Milestone 1: Backend Infrastructure, Auth & Accounts** (PostgreSQL, FastAPI, JWT rotation, Account & Category CRUD, Alembic).
- [ ] **Milestone 2: Android Core, Room & Offline SSOT** (Encrypted Room DB, Hilt DI, Accounts UI, offline storage).
- [ ] **Milestone 3: Transactions & Non-Distorting Split Engine** (Transaction CRUD, Friends directory, Split bill logic, Settlements).
- [ ] **Milestone 4: Android On-Device SMS Detection Pipeline** (SMS receiver, bank regex engine, synthetic test suite, Pending Review UI).
- [ ] **Milestone 5: Budgets, Savings Goals & Financial Analytics** (Category budgets with threshold alerts, goals, dashboard metrics).
- [ ] **Milestone 6: Offline-First Bidirectional Delta Sync** (FastAPI `/sync/push` & `/sync/pull`, Android WorkManager, tombstone deletion).
- [ ] **Milestone 7: Responsive Angular Web Application** (Standalone components, Tailwind CSS, ECharts visualizations).

---

## 🚀 Quick Start (Development Setup)

### Prerequisites
- **Git**
- **Docker Desktop** (for PostgreSQL)
- **Python 3.12+**
- **Android Studio** (Hedgehog or newer) + Android SDK 34
- **Node.js 20+** (for Angular Web)

### 1. Database & Backend Setup
```bash
# Start PostgreSQL via Docker Compose
docker compose up -d db

# Initialize Python virtual environment
cd backend
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1
# Or macOS/Linux: source .venv/bin/activate

# Install dependencies and run migrations
pip install -r requirements.txt
alembic upgrade head

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at: `http://localhost:8000/docs` (Swagger UI).

### 2. Android Setup
1. Open the `android/` directory in **Android Studio**.
2. Allow Gradle to sync dependencies.
3. Run on an Android emulator or physical device running Android 9.0 (API level 28) or higher.

---

## 📚 Technical Documentation Index

| Document | Purpose |
|---|---|
| [**REQUIREMENTS.md**](docs/REQUIREMENTS.md) | Exhaustive functional requirements, user personas, non-functional constraints, and scope boundaries. |
| [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) | System topology, Android Clean Architecture, SMS pipeline, offline sync sequence diagrams, and security model. |
| [**DATABASE_SCHEMA.md**](docs/DATABASE_SCHEMA.md) | Complete PostgreSQL table definitions, `NUMERIC(14,2)` precision, indexes, ERD, and Room mapping. |
| [**API_CONTRACT.md**](docs/API_CONTRACT.md) | RESTful API specifications, JSON request/response structures, JWT family rotation, and sync payloads. |
| [**AGENTS.md**](AGENTS.md) | Strict coding standards and architectural guardrails for AI coding assistants. |
| [**DEVELOPMENT_LOG.md**](DEVELOPMENT_LOG.md) | Architectural decision logs, milestone roadmaps, acceptance criteria, and testing strategies. |

---

## 🔒 Security & Privacy Commitments

- **Zero Raw SMS Upload:** Bank SMS messages are processed locally on the Android device; raw SMS text is never transmitted over the network or saved in server databases.
- **Encrypted Local Storage:** Room SQLite database encrypted using 256-bit SQLCipher with keys protected by the Android Keystore.
- **Strict Monetary Precision:** Fixed-point representations (`NUMERIC(14, 2)` / `BigDecimal` / `Decimal`) are strictly enforced; floating-point money math is prohibited.
- **Token Family Rotation:** Refresh tokens rotate on every exchange; token reuse triggers immediate family revocation.

---

## 📄 License
MIT License. See `LICENSE` for details.
