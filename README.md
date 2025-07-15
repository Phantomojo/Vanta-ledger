# <img src="vanta_ledger_flutter/assets/images/icon-512.png" alt="Vanta Ledger Logo" height="60" style="vertical-align:middle;"> Vanta Ledger

---

> **A next-generation, self-hosted business management and intelligence platform.**
> 
> _Unifying document management, AI-powered analytics, and financial operations into a single, modular command center for the modern enterprise._

---

## 🚀 Ultimate Vision

Vanta Ledger is designed to be the “mission control” for business operations—combining the power of NASA-grade data analysis, AI, and automation with the usability of the world’s best consumer apps. The goal: **turn your document archive and financial data into actionable, real-time business intelligence.**

- **Unified Notion-style Command Center:** All business modules (Companies, Projects, Documents, Ledger, Subcontractors, Users) in one seamless dashboard.
- **AI/NLP at the Core:** Automated document analysis, risk scoring, and semantic search.
- **Offline-First Mobile:** Full-featured finance app for Android/iOS, inspired by MPesa and Instagram.
- **Self-Hosted, Secure, and Extensible:** Your data, your rules—on-prem or cloud.

---

## 🛰️ System Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Web Frontend │    │   Backend    │    │ Paperless-ngx│
│ (React/Vite) │◄──►│ (FastAPI)    │◄──►│ (Docs Mgmt)  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │
        ▼                   ▼
┌──────────────┐      ┌──────────────┐
│  AI/NLP Svc  │      │   Postgres   │
│ (FastAPI)    │      │   Database   │
└──────────────┘      └──────────────┘
        │
        ▼
┌──────────────┐
│   Mobile     │
│ (Flutter)    │
└──────────────┘
```

- **Backend:** Modular FastAPI, SQLAlchemy, Alembic, Paperless-ngx integration
- **AI/NLP Microservice:** FastAPI, spaCy, Llama2, custom ML for extraction, risk, and search
- **Web Frontend:** React/Vite, modular admin panels, analytics, Paperless integration
- **Mobile App:** Flutter, Provider, local DB, offline-first, export/import
- **DevOps:** Docker Compose (Postgres, backend, AI/NLP), .env config, volumes

---

## ✨ Features

### Core Modules
- **Companies, Projects, Documents, Ledger, Tenders, Subcontractors, Users**
- **Document Management:** Paperless-ngx integration, OCR, search, AI extraction
- **Finance & Ledger:** Projects, companies, transactions, analytics, reporting
- **AI/NLP:** Document field extraction, risk scoring, semantic search (FastAPI microservice)
- **Offline-First Mobile:** Flutter app with local DB, Provider state, and export/import
- **Modern Web UI:** React/Vite, modular admin panels, beautiful dark theme
- **Security:** Roles, permissions, audit logs (planned)
- **DevOps:** Docker Compose for full stack, Alembic migrations, .env config

### AI/NLP Capabilities
- **Financial Data Extraction:** Amounts, dates, invoice numbers, tax, confidence scoring
- **Document Classification:** ML-powered (invoices, contracts, receipts, etc.)
- **Entity Recognition:** Companies, people, locations, project codes
- **Duplicate Detection:** Multi-algorithm similarity
- **Risk Scoring:** Multi-factor document risk
- **Trend & Anomaly Detection:** Spending, vendor, project, and outlier analysis
- **Business Intelligence:** Real-time analytics, vendor analysis, project cost tracking
- **Advanced Algorithms:** TF-IDF, fuzzy matching, spaCy NLP, DBSCAN clustering

---

## 🎨 UI/UX & Design Language
- **Notion/MPesa/Instagram-inspired:** Timeline, glassmorphism, high-contrast, modular
- **Premium Elements:** Animated sidebar, micro-interactions, responsive grid, glowing cards
- **Accessibility:** High-contrast, large touch targets, keyboard navigation
- **Custom Icons:** Pinterest-style, SVG/PNG, consistent sizing and spacing
- **Theme System:** Light/dark mode, custom accent colors

---

## 🛠️ DevOps & Deployment

### Docker Compose (Recommended)
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

### Manual Dev Setup
- **Backend:**
  - `cd src/` → `pip install -r requirements.txt` → `alembic upgrade head` → `uvicorn vanta_ledger.main:app`
- **AI/NLP:**
  - `cd src/ai_extractor/` → `pip install -r requirements.txt` → `uvicorn main:app`
- **Web Frontend:**
  - `cd frontend-web/` → `npm install` → `npm run dev`
- **Mobile App:**
  - `cd vanta_ledger_flutter/` → `flutter pub get` → `flutter run`

---

## 🌐 API & Integration

### Key Endpoints
- `GET /api/dashboard` – Analytics and recent activity
- `GET /api/documents` – List/search documents
- `POST /api/extract` – AI/NLP document extraction
- `GET /api/projects` – Project management
- `POST /api/sync` – Manual data sync
- **Paperless-ngx:** REST API for document listing, metadata, and sync

### Data Flow
1. **Document Ingestion:** Paperless-ngx → Integration engine → AI analysis → DB
2. **Real-time Updates:** Background sync, dashboard polling, status indicators
3. **Analytics Generation:** Document metrics, financial trends, project status, risk

---

## 🔒 Security & Compliance
- **Local Processing:** All analysis on your server, no external APIs
- **Encrypted Storage:** Secure document and DB storage
- **Access Control:** User authentication and authorization
- **GDPR Ready:** Data privacy compliance, audit trails, retention policies
- **CORS & Input Validation:** On all endpoints

---

## 📈 Performance & Monitoring
- **Optimizations:** Background processing, caching, pagination, lazy loading
- **Health Checks:** For all services, error logging, performance metrics
- **Monitoring:** Real-time dashboard, alerts for delays, large files, failed docs

---

## 📁 Project Structure

```
Vanta-ledger/
├── src/
│   ├── vanta_ledger/         # Backend (FastAPI, models, routers, schemas)
│   └── ai_extractor/         # AI/NLP microservice (FastAPI, spaCy, ML)
├── frontend-web/             # Web dashboard (React/Vite)
├── vanta_ledger_flutter/     # Mobile app (Flutter)
├── frontend/                 # Legacy Kivy app (being ported)
├── docs/                     # Architecture, vision, feature docs
├── progress_tracker.md       # Living project status
├── docker-compose.yml        # Multi-service orchestration
├── .env.example              # Environment config template
├── .gitignore                # Comprehensive ignore rules
└── ...
```

---

## 🗺️ Development Roadmap

### Current State
- Unified Notion-style command center UI (all admin panels scaffolded)
- Analytics, notifications, AI/NLP, admin tools, and security modules
- All panels ready for backend integration and workflow testing

### Next Phases
1. **Backend API Integration:** Connect all panels to real endpoints, real-time updates
2. **Real Data Wiring:** Replace mock data with live DB and Paperless-ngx data
3. **Advanced AI & Automation:** Live document analysis, risk scoring, semantic search, workflow automation
4. **User Testing & Feedback:** Real-world testing, UI/UX refinement
5. **Documentation & Training:** Complete user/admin docs, onboarding guides

### Future Enhancements
- Real-time notifications, advanced AI models, multi-user support, advanced reporting, accounting/ERP integration, mobile app expansion, handwriting recognition, table extraction, multi-language support

---

## 🧪 Testing & Quality
- **Unit Tests:** For all core modules (backend, AI, mobile)
- **Integration Tests:** API endpoints, data sync, document processing
- **E2E Tests:** Web dashboard, mobile app
- **Performance Benchmarks:** Processing speed, memory, and DB ops
- **Security Audits:** Penetration testing, compliance checks

---

## 🤝 Contributing & Support
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

**Support:**
- Check troubleshooting in docs and logs
- Open an issue or discussion on GitHub
- For advanced help, contact the maintainers

---

## 📚 Appendices

### Kivy Migration
- Legacy Kivy code remains as reference until full migration to web is complete
- See `docs/kivy_garden_install.md` for Kivy chart setup

### Advanced Configuration
- **AI/NLP:** Extend `advanced_document_ai.py` for custom patterns, risk, and entity extraction
- **Sync:** Adjust sync intervals and triggers in backend/AI services
- **UI:** Customize themes, icons, and layouts in frontend-web

### References
- See `docs/`, `AI_SYSTEM_README.md`, `INTEGRATION_README.md`, and `progress_tracker.md` for deep dives

---

**Vanta Ledger: Transforming business data into actionable intelligence.**
