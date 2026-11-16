# Requirements

> **Status:** Draft  
> **Last Updated:** 2026-11-16

---

## 1. Project Overview

Personal Finance Tracker is a cross-platform application that helps users record, categorize, and analyze their expenses and income, providing insights to improve financial habits.

---

## 2. Functional Requirements

### 2.1 Authentication
- [ ] User registration with email & password
- [ ] Login / logout
- [ ] JWT-based session management
- [ ] Password reset via email

### 2.2 Expense Management
- [ ] Add, edit, and delete expense entries
- [ ] Categorize expenses (Food, Transport, Utilities, Entertainment, etc.)
- [ ] Attach notes and optional receipts/images
- [ ] Support multiple currencies

### 2.3 Income Management
- [ ] Add, edit, and delete income entries
- [ ] Categorize income sources (Salary, Freelance, Investment, etc.)

### 2.4 Budgeting
- [ ] Set monthly/weekly budgets per category
- [ ] Alert when spending approaches or exceeds budget

### 2.5 Reporting & Analytics
- [ ] Dashboard with summary cards (total income, total expenses, net balance)
- [ ] Spending breakdown charts (pie, bar)
- [ ] Monthly trend line charts
- [ ] Export reports as CSV / PDF

### 2.6 Sync & Offline Support
- [ ] Offline-first on Android with local Room DB
- [ ] Background sync when connectivity is restored

---

## 3. Non-Functional Requirements

| Category        | Requirement                                                        |
|-----------------|--------------------------------------------------------------------|
| Performance     | API response time < 300 ms (p95) under normal load                |
| Security        | HTTPS everywhere; passwords hashed with bcrypt; no PII in logs    |
| Scalability     | Backend stateless; horizontally scalable via containers            |
| Availability    | 99.5% uptime target for the hosted API                             |
| Accessibility   | WCAG 2.1 AA compliance for the web frontend                        |
| Testability     | ≥ 80% unit-test coverage for backend and Android business logic    |

---

## 4. Out of Scope (v1)

- Bank account / credit card integrations
- Shared/family accounts
- Investment portfolio tracking
