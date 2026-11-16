# 💰 Personal Finance Tracker

A cross-platform personal finance management application — track expenses, income, and budgets from your Android phone or any web browser.

---

## ✨ Features

- 📊 **Dashboard** with real-time income/expense summaries
- 🗂️ **Categorized transactions** with custom categories
- 💼 **Budget tracking** with overspend alerts
- 📈 **Reports & charts** (monthly trends, category breakdown)
- 📱 **Offline-first Android app** with background sync
- 🌐 **Responsive web app** for desktop/tablet use
- 🔐 **Secure JWT authentication** with refresh token rotation

---

## 🏗️ Technology Stack

| Platform | Technology |
|----------|-----------|
| **Android** | Kotlin, Jetpack Compose, Room, Hilt, Coroutines |
| **Web** | Angular 18, TypeScript, TailwindCSS, NgRx |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy, Alembic |
| **Database** | PostgreSQL 16 |
| **Auth** | JWT (python-jose), bcrypt |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |

---

## 📁 Repository Structure

```
Expense Tracker/              ← Monorepo root
├── android/                  ← Kotlin/Android application
├── backend/                  ← Python/FastAPI REST API
├── web/                      ← Angular web application
├── docs/
│   ├── REQUIREMENTS.md       ← Functional & non-functional requirements
│   ├── ARCHITECTURE.md       ← System design & component diagrams
│   ├── DATABASE_SCHEMA.md    ← PostgreSQL table definitions & ERD
│   └── API_CONTRACT.md       ← REST API endpoint reference
├── AGENTS.md                 ← AI coding assistant guidelines
├── DEVELOPMENT_LOG.md        ← Reverse-chronological change log
├── .gitignore
└── README.md                 ← You are here
```

---

## 🚀 Initial Setup

> **Prerequisites:** Git, Android Studio (Hedgehog+), Python 3.12+, Node.js 20+, Docker Desktop

### 1. Clone the repository

```bash
git clone <repository-url>
cd "Expense Tracker"
```

### 2. Backend (FastAPI)

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # fill in your DB credentials
```

### 3. Android

Open `android/` in **Android Studio**. Sync Gradle, then run on an emulator or device.

### 4. Web (Angular)

```bash
cd web
npm install
npm start          # serves on http://localhost:4200
```

### 5. Database (Docker)

```bash
docker compose up -d db
# Then run migrations:
cd backend
alembic upgrade head
```

### 6. Run everything

```bash
docker compose up
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [REQUIREMENTS.md](docs/REQUIREMENTS.md) | What the system must do |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | How the system is structured |
| [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | Database tables and relationships |
| [API_CONTRACT.md](docs/API_CONTRACT.md) | REST API endpoint reference |
| [AGENTS.md](AGENTS.md) | AI assistant coding guidelines |
| [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) | Changelog and decision log |

---

## 🤝 Contributing

1. Read [`AGENTS.md`](AGENTS.md) before writing any code.
2. Create a feature branch: `git checkout -b feat/your-feature`.
3. Follow Conventional Commits: `feat(backend): add budget endpoint`.
4. Open a PR against `main` — CI must pass before merge.
5. Add an entry to [`DEVELOPMENT_LOG.md`](DEVELOPMENT_LOG.md).

---

## 📄 License

MIT — see `LICENSE` for details.
