# 📊 Vanta Ledger – Project Progress Tracker

## ✅ Completed so far:
- Defined big picture & modules:
  - Companies, Projects, Documents, Ledger, Tender pipeline, AI/NLP
- Scaffolded FastAPI backend:
  - FastAPI instance in `main.py`
  - DB connection & session (`database.py`)
  - `.env` config & Alembic setup
- Companies module:
  - SQLAlchemy model
  - Pydantic schemas
  - CRUD router (`routers/companies.py`)
  - Included in `main.py`
- Paperless-ngx running:
  - ~3200 files OCR’d
- Decided folder structure & local self-hosting plan
- **Docker Compose setup:**
  - Postgres, backend, AI/NLP microservice
  - .env, Dockerfile, requirements.txt, volumes
- **AI/NLP microservice scaffolded:**
  - FastAPI, `/extract` endpoint, requirements
- **Web frontend scaffolded:**
  - React/Vite, admin panels, routing, PaperlessPage
- **Legacy Kivy frontend marked for migration**

---

## 🏗 In progress:
- Projects module:
  - Scaffold SQLAlchemy model & relationship to Company
  - Pydantic schemas
  - CRUD router
- Document pipeline:
  - Collect real doc samples
  - Summarize fields to design DB tables & extraction logic
- **API wiring:**
  - Connect frontend panels to backend endpoints
- **Alembic migrations:**
  - Awaiting DB/container setup
- **Paperless-ngx integration:**
  - REST API endpoints, document sync

---

## 🛠 Not started yet:
- Documents module:
  - File upload, versioning, storage path logic
- Ledger module:
  - SQLAlchemy models, CRUD endpoints, link to project/company
- Users/auth module:
  - Simple admin user, later roles
- AI/NLP microservice:
  - spaCy / Llama2 extractor
  - Push extracted fields to DB
- Reports:
  - PDF generator: company profile, tender pack
- Dashboards (Metabase)
- Real-time updates, error handling
- Security, roles, permissions

---

## 📅 TODO / Next steps:
- Finish projects module
- Scaffold documents module
- Write doc extraction prompt for AI pipeline
- Setup dev DB, test data
- Draft ER diagram & update docs
- Fix Docker Compose Postgres issue
- Wire up API to frontend
- Continue AI/NLP integration

---

## 📌 Notes:
- PC specs: i5-650, 4GB RAM, HDD → plan SSD upgrade
- Paperless-ngx: will run alongside FastAPI backend
- Need daily/weekly backups
- Remember: self-hosted, LAN access only 