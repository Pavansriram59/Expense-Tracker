# AGENTS.md — AI Coding Guidelines for Personal Finance Tracker

> This file instructs AI coding assistants (GitHub Copilot, Gemini, Claude, etc.) on the conventions, principles, and guardrails to follow when contributing to this repository.

---

## 1. Project Identity

| Field       | Value                              |
|-------------|------------------------------------|
| Project     | Personal Finance Tracker           |
| Monorepo    | `android/`, `backend/`, `web/`     |
| Docs        | `docs/`                            |
| Primary API | REST / JSON over HTTPS             |

---

## 2. Architectural Principles

1. **Separation of Concerns** — Keep data access, business logic, and presentation in distinct layers. Never let UI or transport concerns bleed into domain logic.
2. **Offline-First on Android** — The Android app treats the local Room database as the source of truth. Remote sync is a background concern.
3. **Stateless Backend** — The FastAPI service must be horizontally scalable. Store no user session state in memory; use the database for refresh tokens.
4. **Contract-First API** — Every new endpoint must be documented in `docs/API_CONTRACT.md` *before* implementation begins.
5. **Schema Migration Safety** — Never drop columns in a single migration. Deprecate first, remove in a later PR.
6. **Feature Flags over Long-Lived Branches** — Prefer feature flags and trunk-based development over multi-week feature branches.

---

## 3. Code Conventions

### 3.1 General
- Prefer **readability** over cleverness.
- Keep functions/methods **single-responsibility** and ≤ 40 lines where possible.
- Write **self-documenting names**; avoid abbreviations unless universally understood (`id`, `url`, `db`).
- All public APIs (functions, classes, endpoints) must have **docstrings / KDoc**.

### 3.2 Backend (Python / FastAPI)
- Follow **PEP 8**; enforced by `ruff`.
- Type hints are **mandatory** for all function signatures.
- Use **Pydantic v2** schemas for all request and response models.
- Business logic lives in `app/services/`; routers in `app/api/` are thin.
- Raise `HTTPException` only in routers, never in services; services raise domain-specific exceptions.
- Use **async/await** throughout; never block the event loop.
- Never log PII (email, passwords, tokens).

### 3.3 Android (Kotlin)
- Follow the **official Kotlin coding conventions**.
- Use **Jetpack Compose** for all new UI; no more XML layouts.
- Apply **MVVM + Clean Architecture**: `data` → `domain` → `presentation`.
- Inject dependencies via **Hilt**; never instantiate repositories or services directly in ViewModels.
- Coroutines with `viewModelScope` for ViewModel work; `withContext(Dispatchers.IO)` for I/O.
- Sealed classes/interfaces for UI state and domain results.

### 3.4 Web (Angular / TypeScript)
- Use **strict TypeScript** (`"strict": true` in tsconfig).
- Prefer **standalone components** (Angular 17+).
- Use the **Angular HTTP Client** with interceptors for auth headers.
- Manage global state via **NgRx** (or signals-based state for simpler slices).
- CSS via **TailwindCSS** utility classes; avoid inline styles.

---

## 4. Security Practices

| Rule | Detail |
|------|--------|
| **No secrets in source** | Use environment variables or a secrets manager. Never commit `.env` files or keys. |
| **Input validation** | Validate at the API boundary (Pydantic). Sanitize before DB writes. |
| **Parameterized queries** | Always use SQLAlchemy ORM or parameterized raw SQL. Never f-string SQL. |
| **Least privilege** | DB user for the app must only have SELECT/INSERT/UPDATE/DELETE — not DDL. |
| **Dependency hygiene** | Pin dependencies with lock files. Run `pip-audit` / `npm audit` in CI. |
| **CORS** | Restrict `allow_origins` to known domains; never `*` in production. |
| **Auth token lifetime** | Access tokens: 15 min. Refresh tokens: 7 days, single-use, stored hashed. |
| **Error messages** | Never expose stack traces or internal details to clients in production. |

---

## 5. Testing Standards

- **Backend:** `pytest` + `httpx` async test client. Target ≥ 80% coverage on `app/services/` and `app/api/`.
- **Android:** JUnit 4/5 for unit tests; Espresso / Compose UI testing for UI flows.
- **Web:** Jasmine/Karma for unit tests; Playwright or Cypress for E2E.
- Every PR must pass existing tests. New features require new tests.
- Do not mock the database in integration tests — use a real PostgreSQL test instance (via Docker).

---

## 6. Git & PR Conventions

- Branch naming: `feat/`, `fix/`, `chore/`, `docs/` prefixes.
- Commit messages follow **Conventional Commits**: `feat(backend): add budget endpoint`.
- Each PR targets `main` and must pass CI before merge.
- Keep PRs small and focused — one concern per PR.
- Update `DEVELOPMENT_LOG.md` with a brief entry for every significant change.

---

## 7. AI Assistant Guardrails

When an AI tool generates code for this project, it **must**:

- ✅ Follow all conventions in this file.
- ✅ Read `docs/API_CONTRACT.md` before generating backend routes or client calls.
- ✅ Read `docs/DATABASE_SCHEMA.md` before generating models or migrations.
- ✅ Generate tests alongside implementation code.
- ✅ Flag potential security issues explicitly in comments or PR description.
- ❌ **Never** generate code that stores plain-text passwords.
- ❌ **Never** commit secrets, tokens, or credentials.
- ❌ **Never** bypass the domain/service layer to query the DB directly from a router.
- ❌ **Never** introduce a new dependency without documenting the rationale.
- ❌ **Never** silently swallow exceptions with bare `except: pass`.

---

## 8. Documentation Requirements

Every change that affects behavior must update at least one of:

- `docs/REQUIREMENTS.md` — if a requirement changes.
- `docs/ARCHITECTURE.md` — if a component or data flow changes.
- `docs/DATABASE_SCHEMA.md` — if a table or column changes.
- `docs/API_CONTRACT.md` — if an endpoint is added, changed, or removed.
- `DEVELOPMENT_LOG.md` — always, for significant changes.
