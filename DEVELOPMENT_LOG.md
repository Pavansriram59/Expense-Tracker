# Development Log

> Reverse-chronological log of significant changes, decisions, and milestones.  
> Add an entry for every PR or notable session.

---

## Format

```
## YYYY-MM-DD — <Short Title>
**Author:** <name or alias>
**Scope:** android | backend | web | docs | infra | all

### What changed
- Bullet points describing what was done.

### Decisions made
- Any architectural or design decisions taken and the reasoning.

### Next steps
- What comes next.
```

---

## 2026-11-16 — Repository Bootstrap

**Author:** Initial Setup  
**Scope:** all

### What changed
- Initialized Git repository.
- Created monorepo folder structure: `android/`, `backend/`, `web/`, `docs/`.
- Added placeholder documentation: `REQUIREMENTS.md`, `ARCHITECTURE.md`, `DATABASE_SCHEMA.md`, `API_CONTRACT.md`.
- Added `AGENTS.md` with AI coding guidelines and project conventions.
- Added `.gitignore` for Kotlin/Android, Python/FastAPI, Angular, and IDE files.
- Added root `README.md`.

### Decisions made
- Chose a **monorepo** layout to keep all platform code co-located and ease cross-cutting changes (schema, API contract).
- Documentation-first approach: all core docs drafted before any implementation begins.
- AI guidelines encoded in `AGENTS.md` to ensure consistent code generation across assistants.

### Next steps
- Scaffold Android project (Kotlin, Jetpack Compose, Hilt, Room).
- Scaffold FastAPI backend with project structure and Docker setup.
- Scaffold Angular web app with standalone components and TailwindCSS.
- Implement database migrations with Alembic.
