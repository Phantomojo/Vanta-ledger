# <img src="vanta_ledger_flutter/assets/images/icon-512.png" alt="Vanta Ledger Logo" height="60" style="vertical-align:middle;"> Vanta Ledger

![Build](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Web%20%7C%20Mobile%20%7C%20Desktop-purple)

---

> **A modern, self-hosted business management system with unified dashboard, AI/NLP, analytics, and offline-first mobile app.**

---

## 🏗️ Project Structure

- **Backend (FastAPI):** `src/vanta_ledger/`
- **AI/NLP Microservice:** `src/ai_extractor/`
- **Web Frontend (React/Vite):** `frontend-web/`
- **Mobile App (Flutter):** `vanta_ledger_flutter/`
- **Legacy Kivy App:** `frontend/` (being ported to web)
- **Docs & Progress:** `docs/`, `progress_tracker.md`, `technical_architecture.md`

---

## ✨ Features

- **Unified Command Centre:** Notion/MPesa-inspired dashboard for all business modules
- **Document Management:** Paperless-ngx integration, OCR, search, and AI extraction
- **Finance & Ledger:** Projects, companies, transactions, analytics, and reporting
- **AI/NLP:** Document field extraction, risk scoring, semantic search (FastAPI microservice)
- **Offline-First Mobile:** Flutter app with local DB, Provider state, and export/import
- **Modern Web UI:** React/Vite, modular admin panels, beautiful dark theme
- **Security:** Roles, permissions, audit logs (planned)
- **DevOps:** Docker Compose for full stack, Alembic migrations, .env config

---

## 🚀 Quick Start (Docker Compose)

```sh
# Clone the repo
https://github.com/Phantomojo/Vanta-ledger.git
cd Vanta-ledger

# Copy and edit .env if needed
cp .env.example .env

# Build and run all services
sudo docker compose up --build
```

- Backend: http://localhost:8500
- AI/NLP: http://localhost:8600
- Postgres: localhost:5432
- Web frontend: (see frontend-web/ for dev server)

---

## 🛠️ Manual Dev Setup

- **Backend:**
  - Python 3.11+, FastAPI, SQLAlchemy, Alembic
  - `cd src/` → `pip install -r requirements.txt` → `alembic upgrade head` → `uvicorn vanta_ledger.main:app`
- **AI/NLP:**
  - `cd src/ai_extractor/` → `pip install -r requirements.txt` → `uvicorn main:app`
- **Web Frontend:**
  - `cd frontend-web/` → `npm install` → `npm run dev`
- **Mobile App:**
  - `cd vanta_ledger_flutter/` → `flutter pub get` → `flutter run`

---

## 📦 What’s Tracked in Git

- All source code, configs, and documentation
- **NOT tracked:**
  - `raw_docs/`, `logs/`, `cache/`, `exports/`, `vanta_ledger.db`, `node_modules/`, `__pycache__/`, `.venv/`, build artifacts, IDE files
  - See `.gitignore` for full list

---

## 📄 Documentation

- **progress_tracker.md:** Living project status and next steps
- **docs/technical_architecture.md:** System architecture, migration plan, and UI/UX vision
- **INTEGRATION_README.md:** Integration details for Paperless-ngx and other services

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Original concept by Phantomojo
- Developed with assistance from Manus AI
- Inspired by Notion, MPesa, Instagram, and modern fintech apps
