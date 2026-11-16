# Architecture

> **Status:** Draft  
> **Last Updated:** 2026-11-16

---

## 1. High-Level Overview

```
┌──────────────┐     HTTPS/REST      ┌───────────────────┐
│  Android App │ ◄──────────────────► │                   │
│  (Kotlin)    │                      │  FastAPI Backend   │
└──────────────┘                      │  (Python)         │
                                      │                   │
┌──────────────┐     HTTPS/REST      │  ┌─────────────┐  │
│   Web App    │ ◄──────────────────► │  │  PostgreSQL  │  │
│  (Angular)   │                      │  └─────────────┘  │
└──────────────┘                      └───────────────────┘
```

---

## 2. Technology Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Android     | Kotlin, Jetpack Compose, Room, Hilt |
| Web         | Angular 18, TypeScript, TailwindCSS |
| Backend     | Python 3.12, FastAPI, SQLAlchemy    |
| Database    | PostgreSQL 16                       |
| Auth        | JWT (python-jose), bcrypt           |
| Hosting     | Docker / Docker Compose (self-host) |
| CI/CD       | GitHub Actions                      |

---

## 3. Component Architecture

### 3.1 Backend (FastAPI)
```
backend/
├── app/
│   ├── api/          # Route handlers (routers)
│   ├── core/         # Config, security, dependencies
│   ├── models/       # SQLAlchemy ORM models
│   ├── schemas/      # Pydantic request/response schemas
│   ├── services/     # Business logic layer
│   └── main.py       # Application entry point
├── tests/
├── alembic/          # Database migrations
└── Dockerfile
```

### 3.2 Android (Kotlin)
```
android/
└── app/
    └── src/
        └── main/
            ├── data/         # Room DB, repositories, remote data sources
            ├── domain/       # Use cases, domain models
            ├── presentation/ # ViewModels, Compose UI screens
            └── di/           # Hilt modules
```

### 3.3 Web (Angular)
```
web/
└── src/
    └── app/
        ├── core/       # Auth guards, interceptors, singleton services
        ├── shared/     # Reusable components, pipes, directives
        └── features/   # Feature modules (dashboard, expenses, reports)
```

---

## 4. Data Flow

1. **Client** sends authenticated HTTP request (Bearer JWT).
2. **FastAPI** validates token → resolves current user.
3. **Service layer** applies business rules, calls repository.
4. **SQLAlchemy** executes query against **PostgreSQL**.
5. Response serialized via **Pydantic** schema → returned to client.

---

## 5. Security Architecture

- All traffic over TLS 1.2+.
- Passwords hashed with **bcrypt** (cost factor ≥ 12).
- Short-lived access tokens (15 min) + refresh tokens (7 days).
- Refresh tokens stored server-side; invalidated on logout.
- Rate limiting on auth endpoints.
- Input validation at the API boundary (Pydantic).

---

## 6. Deployment Architecture (MVP)

```
Docker Compose (single host)
├── service: api        (FastAPI + Uvicorn)
├── service: db         (PostgreSQL)
└── service: web        (Nginx serving Angular build)
```

Future: Kubernetes / managed cloud (phase 2).
