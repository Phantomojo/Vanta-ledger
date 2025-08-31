Project: Vanta Ledger — System Overview (Junie)

Purpose
- Provide a concise, accurate map of the repository so contributors can quickly navigate and operate the system.
- Summarize backend, frontend, data flows, security, and operations.

High-level Summary
- Full‑stack financial/document management platform.
- Backend: Python 3.12+, FastAPI, Prometheus metrics, Redis, PostgreSQL, MongoDB.
- Frontend: React + TypeScript (Vite), Axios API client, AuthContext with JWT.
- Services: OCR/AI document processing (pytesseract, pdf2image, PyMuPDF, python-docx, Pillow), optional spaCy NER, local LLM integration toggle.
- DevOps: Docker/Docker Compose, .env conventions, scripts, monitoring hooks.

Backend (src/vanta_ledger)
- Entry points
  - main.py: Primary FastAPI application.
    - Startup: settings.validate_required_config(), initialize_services().
    - Middleware: LoggingMiddleware, SecurityHeadersMiddleware, RateLimitMiddleware, CORS.
    - Health and metrics: GET /health, GET /metrics (Prometheus).
    - Test endpoints (for frontend scaffolding and diagnostics):
      - GET /test-companies, GET /test-documents, GET /test-ledger, POST /test-upload-document.
    - Includes multiple routers (see Routers section).
  - main_simple.py, simple_main.py: Reduced variants for simplified runs/debugging.

- Configuration (config.py)
  - Environment-based settings. Key vars: MONGO_URI, POSTGRES_URI, REDIS_URI, SECRET_KEY.
  - Production requires SECRET_KEY; MONGO_URI and POSTGRES_URI required always.
  - Rate-limiting defaults, password policy flags, CORS origins, upload/processed directories (data/uploads, data/processed_documents), local LLM flags.

- Security & Auth (auth.py)
  - JWT (HS256) with access/refresh, passlib password hashing.
  - Redis-backed token blacklist (jti-based).
  - Role dependencies: require_role, current_user dependency helpers.
  - AuthService: create/verify tokens, authenticate_user (stubs + user service integration).

- Middleware (middleware.py)
  - RateLimitMiddleware: per-IP quotas (minute/hour) with headers.
  - SecurityHeadersMiddleware: HSTS, CSP (lenient for /docs), X-Frame-Options, X-Content-Type-Options, Referrer/Permissions policies.
  - LoggingMiddleware: request/response logs, timing.

- Databases
  - database.py: connectors to PostgreSQL (psycopg2), MongoDB (pymongo), Redis.
  - database_init.py, hybrid_database.py present for initialization/hybrid usage (see codebase for details).

- Services
  - services/document_processor.py: advanced upload/extraction pipeline.
    - Supported types: pdf, docx/doc, txt, png/jpg/jpeg/tiff/bmp.
    - OCR toolchain (enabled if libs installed). spaCy NER optional.
    - Resolves storage paths relative to project root, ensures directories exist.
    - Extraction helpers and financial patterns (amounts, percent, dates, phone, email, URL).

- Routers (src/vanta_ledger/routes)
  - auth (prefix /auth): login (form), logout (blacklist), refresh, register (form).
  - companies (prefix /companies): GET list (static test data), GET by id (DB-backed pattern).
  - documents (prefix /upload/documents): Upload/CRUD for documents (see file).
  - enhanced_documents (prefix /api/v2/documents): v2 endpoints for richer document workflows.
  - extracted_data (prefix /extracted-data): search/analytics/export endpoints on extracted items.
  - financial (prefix /api/v2/financial): financial domain actions.
  - ledger (prefix /ledger): entries, summaries.
  - local_llm (prefix /api/v2/llm): local LLM utilities.
  - notifications (/notifications), paperless_integration (/paperless), projects (/projects), users (/users).
  - simple_auth: convenience endpoint used by frontend at POST /simple-auth.

Frontend (frontend/frontend-web)
- Tech: React + TypeScript.
- API client (src/api.ts): Axios baseURL http://localhost:8500
  - JWT interceptor reads localStorage key jwt_token, attaches Authorization: Bearer <token>.
  - Global 401 handler clears token and redirects to /signin.
  - Endpoints intentionally use test routes for data hydration:
    - Companies: GET /test-companies
    - Documents: GET /test-documents, POST /test-upload-document
    - Ledger: GET /test-ledger
    - Auth: POST /simple-auth (query params), GET /auth/me, /auth/register
    - Extracted data, analytics, projects, ledger CRUD map to standard routes.
- AuthContext (src/context/AuthContext.tsx):
  - login() persists jwt_token, maps user basics.
  - On load, attempts GET /auth/me if token exists; clears invalid token.
- Representative pages/components (by filenames):
  - pages/Ledger.tsx, pages/Projects.tsx
  - Dashboard/DocumentComplianceWidget.tsx
  - tables/BasicTables/BasicTableOne.tsx

Operations & Deployment
- Env files: env.example, env.production.example
- Docker: Dockerfile, Dockerfile.production; docker-compose.yml and docker-compose.*.yml
- Nginx dir present for reverse proxy configuration.
- Scripts for starting services: start_backend.py, launch_vanta_ledger.py, start_vanta.sh, start_vanta_corrected.sh, stop_vanta.sh.
- Monitoring: Prometheus endpoint at /metrics; security monitors/scripts available.

Security Highlights
- Strong default headers via middleware; CSP accommodates Swagger docs.
- SECRET_KEY enforced in non-debug.
- JWT blacklist with Redis; rate limiting per IP.
- Password policy settings configurable via env.
- Extensive security documentation in repository (multiple SECURITY*.md docs).

Data & Storage
- Uploads: data/uploads
- Processed docs: data/processed_documents
- Logs: logs/app.log (ensured by middleware logging setup)

Testing
- Numerous test files in project root and tests directory (e.g., test_backend_server.py, test_backend_integration.py, test_llm_*.py, test_mongodb_simple.py, test_minimal.py).
- Quick check: python3 -m pytest (ensure env vars set or use simple_main/test endpoints where applicable).

Local Development Quick Start (typical)
- Ensure Python 3.12 virtualenv and dependencies installed (see requirements.txt / pyproject.toml).
- Set environment variables (copy env.example to .env and adjust):
  - MONGO_URI, POSTGRES_URI, REDIS_URI
  - SECRET_KEY (required in production)
  - CORS and rate limit settings as needed
- Run backend (examples):
  - uvicorn vanta_ledger.main:app --host 0.0.0.0 --port 8500
  - or use provided start scripts.
- Run frontend:
  - cd frontend/frontend-web && npm install && npm run dev
- Visit http://localhost:5173 (frontend) and backend at http://localhost:8500

Notes & Tips
- The /test-* endpoints provide ready data for the frontend without a running DB.
- The GitHub Models router exists but is disabled in main.py pending import resolution.
- Local LLM is optional and controlled via settings (ENABLE_LOCAL_LLM, model paths, etc.).
- If you encounter 422 or auth issues during early dev, verify the frontend uses the simple_auth flow and that jwt_token is stored.

Ownership & Next Steps (for contributors)
- Backend: expand static endpoints in companies/documents/ledger to DB-backed implementations using database.py.
- Centralize auth/user persistence with services.user_service and models.user_models.
- Tighten CSP if embedding third-party content; ensure CORS origins reflect deployed URLs.
- Add integration tests for document_processor with available test files (test_invoice.txt etc.).
