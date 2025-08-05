# Vanta Ledger - Technical Architecture (June 2024)

## System Overview
- **Unified Command Centre:** Notion-style, high-contrast, modular dashboard (web, mobile, legacy Kivy)
- **Backend (FastAPI):** Modular API, SQLAlchemy models, Alembic migrations, Paperless-ngx integration
- **AI/NLP Microservice:** FastAPI, document field extraction, risk scoring, semantic search (planned: spaCy, Llama2)
- **Web Frontend:** React/Vite, admin panels, analytics, Paperless integration, modern UI/UX
- **Mobile App:** Flutter, Provider state, local DB, offline-first, export/import
- **Legacy Kivy App:** Being ported to web; remains as reference
- **DevOps:** Docker Compose (Postgres, backend, AI/NLP), .env config, volumes

## Integration Points
- **Paperless-ngx:** REST API endpoints for document listing, metadata, and sync
- **AI/NLP:** `/extract` endpoint for document field extraction, risk scoring, and semantic search
- **Frontend:** All admin panels ready for backend API integration (CRUD, analytics, AI, etc.)

## Migration Plan
- Kivy dashboard and screens are being ported to the web frontend (`frontend-web/`) using React and Vite
- Legacy Kivy code will remain as reference until migration is complete

| Kivy Section/Component      | React Page/Component         |
|----------------------------|------------------------------|
| CommandCenterScreen        | DashboardPage, Sidebar, Topbar|
| Dashboard (section)        | DashboardHome                |
| Documents (section)        | DocumentsPage                |
| Ledger (section)           | LedgerPage                   |
| Projects (section)         | ProjectsPage                 |
| Companies (section)        | CompaniesPage                |
| Subcontractors (section)   | SubcontractorsPage           |
| Analytics (section)        | AnalyticsPage, Charts        |
| Review Tools (section)     | ReviewToolsPage              |
| Settings (section)         | SettingsPage                 |
| Paperless (section)        | PaperlessStatusPage          |
| Force Scan (section)       | ForceScanPage                |
| Admin (section)            | AdminPanel                   |
| Custom Components (charts, dialogs, forms, navigation, transaction_card) | Reusable React components |

## Docker Compose & DevOps
- **Services:**
  - `postgres`: Main DB
  - `backend`: FastAPI app
  - `ai_extractor`: AI/NLP microservice
- **Volumes:**
  - `pgdata` for persistent Postgres storage
- **.env:**
  - Centralized config for DB, API, and service URLs

## Roadmap & Next Steps
1. API wiring: Connect all panels to backend endpoints
2. Real-time updates, error handling
3. Advanced AI: Integrate live document analysis and risk scoring
4. Workflow automation: Compliance, notifications, routine tasks
5. Security: Roles, permissions, audit logs

## UI/UX Vision
- Unified dashboard for all business features
- Sidebar/topbar navigation, modular panels
- High-contrast, modern, responsive design
- Inspired by Notion, MPesa, Instagram

**All new development targets the unified dashboard. Legacy Kivy screens are being ported or retired.**
