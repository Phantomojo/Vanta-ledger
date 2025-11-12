# 05 - API Endpoints

## 17 Route Modules (src/vanta_ledger/routes/)

### Core
- **auth.py** - Login, register, token refresh
- **users.py** - User CRUD, profile management
- **companies.py** - Multi-tenant company management

### Financial
- **financial.py** - Transactions, accounts
- **ledger.py** - Ledger entries, balances
- **projects.py** - Project tracking

### Documents
- **documents.py** - Upload, retrieve, delete
- **enhanced_documents.py** - Advanced features
- **extracted_data.py** - OCR results
- **paperless_integration.py** - External integration

### Analytics & AI
- **analytics.py** - Dashboards, reports
- **ai_analytics.py** - AI-powered insights
- **local_llm.py** - LLM integration

### Other
- **notifications.py** - User notifications
- **config.py** - Configuration endpoints
- **simple_auth.py** - Frontend auth compatibility

## API Base: `http://localhost:8500`
## Docs: `http://localhost:8500/docs`

## Next: Database Schema (`06-database-schema.md`)
