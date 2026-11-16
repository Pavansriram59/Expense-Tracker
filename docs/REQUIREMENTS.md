# Requirements & Specification

> **Project:** Personal Finance Tracker (Axio-inspired)  
> **Status:** Approved Architecture Draft  
> **Last Updated:** 2026-11-16  
> **Platforms:** Android (Native, Offline-First) ➔ Backend (FastAPI, Modular Monolith) ➔ Web (Angular, Responsive)

---

## 1. Executive Summary & Vision

The **Personal Finance Tracker** is a privacy-first, offline-first personal financial management platform designed to automate and simplify daily money management. Inspired by apps like Axio (formerly Walnut), the platform automatically digests transaction updates (primarily via local SMS parsing on Android), enables real-world expense splitting with friends without financial distortion, tracks accounts across bank, credit card, cash, and UPI channels, and provides actionable analytics and budget safeguards.

### Core Value Propositions
1. **Frictionless Ingestion:** Automated detection of debits, credits, UPI payments, and card swipes from bank SMS messages with local, on-device parsing.
2. **Accurate Real-World Accounting:** Mathematical separation between personal expenses, gross bank debits, and receivables from friends (splitting a dinner does not artificially inflate personal expense or income upon settlement).
3. **Resilient Offline Architecture:** Complete autonomy on Android with Room; seamless bidirectional delta synchronization with a centralized FastAPI/PostgreSQL backend.
4. **Absolute Privacy:** Raw SMS messages never leave the device. Only structured, user-confirmed financial records synchronize with the cloud.
5. **Multi-Account Aggregation:** Unified dashboard tracking liquid bank balances, credit card liabilities, cash on hand, and digital wallets.

---

## 2. User Personas & Core Workflows

### 2.1 Personas
- **The Digital Spender (P1):** Makes 10–20 daily UPI and card transactions. Needs automated tracking without manual entry after every coffee or ride.
- **The Group Sharer (P2):** Frequently pays for shared group dinners, rent, or utilities and needs to track who owes what, record partial settlements, and keep net personal spending accurate.
- **The Budget Conscious (P3):** Sets category spending limits, tracks monthly savings goals, and needs alerts before overspending.
- **The Privacy-Sensitive User (P4):** Refuses to upload SMS messages or grant bank credentials to cloud aggregators; expects local data sovereignty.

### 2.2 Critical User Journeys
1. **SMS Transaction Capture & Split:** User pays ₹2,400 via UPI for a dinner with 3 friends. App detects bank SMS locally, creates a pending transaction, alerts user via notification. User confirms category as "Food & Dining", selects "Split Equally with 3 Friends". The app records ₹600 as user's personal expense and ₹1,800 as money owed across friends.
2. **Settlement Collection:** A friend sends ₹600 via UPI. User records settlement. Account balance increases by ₹600, friend's debt decreases to ₹0, and net income is unchanged.
3. **Offline Ingestion & Subsequent Sync:** User enters transactions and edits budgets during an offline flight. Upon reconnecting, WorkManager delta-syncs local mutations to the backend with zero data loss.

---

## 3. Functional Requirements (FR)

### FR-1: Account & Asset Management
- **FR-1.1 Account Types:** Support Bank Accounts (Savings/Current), Credit Cards, Cash Wallets, and Digital/UPI Wallets.
- **FR-1.2 Account Metadata:** Store account name, institution, account number suffix (last 4 digits for SMS matching), currency code (default: `INR`), current balance, color, and icon.
- **FR-1.3 Credit Card Specifics:** Store credit limit, available credit, statement billing cycle day, and payment due date.
- **FR-1.4 Account Transfers:** Support internal transfers (e.g., ATM withdrawal: Bank ➔ Cash; Credit Card bill payment: Bank ➔ Credit Card). Transfers must not count as income or expense.
- **FR-1.5 Balance Reconciliation:** Allow manual balance adjustments with an automatic ledger reconciliation entry.

### FR-2: Transaction Management
- **FR-2.1 Core Types:** Support `EXPENSE`, `INCOME`, and `TRANSFER`.
- **FR-2.2 Transaction Fields:** Mandatory ID (UUIDv7), account reference, category reference, gross amount, personal amount, transaction timestamp, type, status (`CONFIRMED`, `PENDING_REVIEW`, `DRAFT`), notes, tags, and receipt attachment metadata.
- **FR-2.3 Hierarchical Categorization:** System default categories and custom user-defined categories with subcategories (e.g., `Food & Dining` ➔ `Groceries`, `Restaurants`).
- **FR-2.4 Search & Filtering:** Filter by account, date range, category, transaction type, tag, amount range, and split status. Full-text search on merchant and notes.
- **FR-2.5 Soft Deletion:** Deletions mark `is_deleted = TRUE` to ensure deletion propagation across devices during synchronization.

### FR-3: SMS-Based Automated Transaction Detection (Android Only)
- **FR-3.1 Ingestion Pipeline:** Broadcast receiver listening to incoming SMS + on-demand historical inbox scanner.
- **FR-3.2 Regex & Heuristic Parser:**
  - Extract: Transaction Type (`DEBIT`, `CREDIT`, `REFUND`), Gross Amount, Currency, Merchant/VPA identifier, Timestamp, Account/Card last 4 digits, Reference/UTR number.
  - Supported formats: Major Indian banks (HDFC, SBI, ICICI, Axis, Kotak, PNB, etc.), credit card networks, and UPI gateways.
  - Filter out OTPs, promotional spam, balance alerts, and non-financial communications.
- **FR-3.3 Deduplication Engine:** Compute a cryptographic fingerprint from `(account_suffix, amount, date_within_15min_window, ref_number)`. Ignore duplicate SMS messages.
- **FR-3.4 Pending Confirmation Queue:**
  - Detected transactions enter a "Review Queue" as `PENDING_REVIEW`.
  - Push actionable notification: *"Spent ₹450 at Starbucks. Confirm category or split?"*
  - Auto-confirm option: Users can enable auto-confirmation for trusted regular merchants.
- **FR-3.5 Privacy & Security Guardrail:**
  - **Zero SMS Cloud Upload:** Raw SMS text is processed strictly on-device in the Android sandbox. Raw SMS bodies are never sent over the network or saved in remote databases.
  - **Synthetic Test Fixture:** Parser unit tests must run against synthetic SMS fixtures without requiring live device permissions.
- **FR-3.6 Policy Compliance Architecture:**
  - Package SMS functionality behind an `SmsIngestionService` interface.
  - Support alternative ingestion (manual SMS snippet paste, Notification Listener service) if Google Play Store policy restricts `RECEIVE_SMS` / `READ_SMS` permissions.

### FR-4: Split Expenses & Friends Ledger
- **FR-4.1 Friends Directory:** Maintain a local directory of friends (Name, Phone, Email, Notes).
- **FR-4.2 Splitting Mechanisms:**
  - **Equal Split:** Divide remaining amount equally among N participants.
  - **Exact Amounts:** Specify exact currency amounts per participant (sum must equal total).
  - **Percentage Split:** Allocate percentages (sum must equal 100.0%).
  - **Shares/Ratios:** Allocate arbitrary share units (e.g., 2 shares vs 1 share).
- **FR-4.3 Core Financial Rules for Splits:**
  - The gross bank transaction amount remains intact in the account ledger.
  - The user's personal expense is isolated (`personal_amount = gross_amount - sum(friend_shares)`).
  - Friend shares are registered in the `split_bill_members` ledger as receivables (`ACCOUNTS_RECEIVABLE`).
  - Money received from friends during settlement is **not** treated as income; it is treated as a debt reduction and asset transfer.
  - If a friend pays on behalf of the user, the user's personal expense is recorded with a corresponding liability (`ACCOUNTS_PAYABLE`).
- **FR-4.4 Settlements:**
  - Support full and partial settlements.
  - Record the settling account (e.g., "Received ₹500 from Rahul into HDFC Bank").
  - Settlement history ledger maintaining full auditability.

### FR-5: Budgets & Spending Safeguards
- **FR-5.1 Granular Budgets:** Monthly and weekly spending targets per category, parent category, or global overall spending.
- **FR-5.2 Threshold Notifications:** Proactive alerts at 50%, 80%, and 100% of budget consumption.
- **FR-5.3 Rollover Budgets:** Optional configuration to roll over unspent budget or deficit to the subsequent period.
- **FR-5.4 Personal vs Gross Budgeting:** Budgets calculate against the user's **personal expense**, excluding split amounts owed by friends.

### FR-6: Savings Goals
- **FR-6.1 Goal Definitions:** Title, target amount, target date, priority, and linked savings account or virtual vault.
- **FR-6.2 Contribution Tracking:** Manual deposits or automated allocations linked to specific income or savings transactions.
- **FR-6.3 Progress Metrics:** Visual completion percentages, required monthly savings rate to hit target date, and projection warnings if off-track.

### FR-7: Recurring Bills & Subscriptions
- **FR-7.1 Cadence Support:** Daily, Weekly, Monthly, Quarterly, Bi-annual, and Annual recurrences.
- **FR-7.2 Due-Date Reminders:** Native Android alarms / WorkManager notifications 3 days, 1 day, and on the morning of bill due dates.
- **FR-7.3 Execution Modes:** Manual confirmation prompt vs auto-posting on due date.

### FR-8: Dashboard & Financial Analytics
- **FR-8.1 Real-Time Net Worth & Liquid Balance:** Total liquid funds across all bank/cash/wallet accounts minus credit card payables.
- **FR-8.2 Cash Flow Velocity:** Income vs. Personal Expenses for current month with previous period comparison.
- **FR-8.3 Categorical Breakdown:** Interactive Donut/Pie charts with drill-down into subcategories and merchant frequency.
- **FR-8.4 Historical Trends:** Daily, weekly, monthly, and annual spending curves with average daily burn rate.

### FR-9: Future AI Capabilities (Architectural Hook Ready)
- **FR-9.1 Categorization Engine:** Local heuristic rules in Phase 1; upgrade path to local lightweight embeddings/LLM backend API in Phase 4.
- **FR-9.2 Natural Language Query Contract:** API schema ready for queries such as *"What was my total spend on dining last month?"*.
- **FR-9.3 Anomaly Detection:** Flag duplicate charges, unusual merchant billings, and unexpected subscription price spikes.

---

## 4. Non-Functional Requirements (NFR)

### NFR-1: Performance & Responsiveness
- **API Latency:** p95 < 200 ms for transaction listings; p99 < 500 ms for complex analytics queries.
- **Android Cold Startup:** < 1.2 seconds on mid-tier Android devices (e.g., Snapdragon 600-series / Dimensity 700).
- **Smooth UI:** Stable 60/120 fps Jetpack Compose rendering with zero jank during list scrolling.
- **Local DB Query Time:** Room database queries must complete in < 25 ms on the main thread via Coroutines `Dispatchers.IO`.

### NFR-2: Offline-First Operation & Data Sync
- **Full Offline Autonomy:** 100% of core actions (create/edit/delete transactions, accounts, categories, budgets, splits) must succeed without an internet connection.
- **Delta Sync:** The sync protocol sends only modified records using timestamp high-watermarks (`last_sync_timestamp`) and UUIDv7 identifiers.
- **Conflict Resolution:** Deterministic Last-Write-Wins (LWW) resolution based on UTC client update timestamps, with server-side validation against illegal states.
- **Tombstones:** Soft deletions use tombstone markers (`is_deleted = TRUE`, `deleted_at = TIMESTAMPTZ`) to propagate deletions cleanly.

### NFR-3: Security, Privacy & Data Protection
- **Storage Encryption:** Local Room SQLite database encrypted using SQLCipher. Sensitive credentials (tokens, user pins) stored in Android Keystore / EncryptedSharedPreferences.
- **Network Security:** TLS 1.3 mandatory. Strict Certificate Pinning in production Android builds.
- **Authentication:** Short-lived JWT access tokens (15 minutes) with rotating refresh tokens (7 days). Token family invalidation on detected token reuse.
- **Zero Raw PII/SMS Ingestion:** Raw SMS content is stripped and discarded after regex extraction. The server receives only structured transaction data.
- **Financial Precision:** Floating-point data types (`float`, `double`) are **prohibited** for monetary values. All amounts must be stored as exact `NUMERIC(14, 2)` or integer minor units (paise/cents).

### NFR-4: Code Quality & Architecture Standards
- Strict compliance with `AGENTS.md` guidelines.
- Clean Architecture on Android: Presentation (Compose) ➔ Domain (Use Cases) ➔ Data (Room + Retrofit).
- Modular Monolith on Backend: Thin FastAPI routers ➔ Service layer business logic ➔ SQLAlchemy ORM / Alembic.
- Strict typing: Python type hints validated by `mypy` and `ruff`; Kotlin strict null safety.
- Test Coverage: Minimum 80% coverage on backend services and Android domain use cases.

---

## 5. Scope Boundaries

| Dimension | In Scope (v1 & v2) | Deferred / Out of Scope (Future) |
|---|---|---|
| **Platforms** | Android (Kotlin Compose) + Backend (FastAPI) + Web (Angular) | iOS (Swift), Desktop Native |
| **Banking Integration** | Local SMS regex ingestion & manual entry | Direct Bank Open APIs / Account Aggregator (Setu/Anumati) |
| **Currencies** | Multi-currency storage with base currency conversion | Real-time live forex trading feeds |
| **Split Operations** | User + Friends ledger, partial settlements | In-app peer-to-peer UPI money transfer execution |
| **Investments** | Manual asset entry & net worth tracking | Real-time stock broker / mutual fund portfolio sync |
| **AI Features** | Rule-based categorization & clean API contracts | Self-hosted fine-tuned LLM inference pipeline |

---

## 6. Assumptions & Unresolved Questions

### 6.1 Assumptions
1. The user will run the Android application on Android 9.0 (API level 28) or higher.
2. The user primarily transacts in India (INR) where transactional bank SMS messages follow standard structural patterns (debited by, credited by, VPA, Avail Bal, Ref/UTR).
3. The backend will initially be self-hosted or deployed via Docker Compose on a single Linux VPS (e.g., 2 vCPU, 4GB RAM) with PostgreSQL.

### 6.2 Open Questions for Development
1. **Google Play Store Policy:** If the target distribution is Google Play Store, will Google grant the `RECEIVE_SMS` financial exception?  
   *Mitigation:* Build a modular ingestion interface that can swap between `SmsBroadcastReceiver`, `NotificationListenerService` (reading bank notification banners), and a local clipboard/paste parser.
2. **Multi-device Active Sync:** If the user updates an account on Web and Android simultaneously while offline, should field-level merging be supported?  
   *Resolution for v1:* Entity-level Last-Write-Wins (LWW) is adopted for simplicity and safety; split transactions use immutable ledger events to prevent partial overwrites.
3. **SMS History Ingestion:** When first installed, should the app offer to parse the last 30/90 days of SMS history?  
   *Resolution:* Yes, with a progress bar, duplicate filtering, and batch grouping into the Pending Review queue.
