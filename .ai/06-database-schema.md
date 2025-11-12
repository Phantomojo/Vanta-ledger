# 06 - Database Schema

## PostgreSQL Models (src/vanta_ledger/models/)

### Users (`user_models.py`)
- UserDB: id, username, email, hashed_password, role, company_id
- Roles: "admin", "user", "GOD"

### Companies
- Company: id, name, settings, created_at
- Multi-tenant isolation via company_id foreign keys

### Financial (`financial_models.py`)
- Transaction: id, amount, type, company_id, user_id, date
- Account: id, name, balance, company_id
- Project: id, name, budget, company_id

### Documents (`document_models.py`)
- Document: id, filename, file_path, company_id, upload_date
- ExtractedData: id, document_id, extracted_text, entities

## MongoDB Collections
- documents (file storage)
- ai_results (LLM analysis)
- processing_queue

## Redis Keys
- session:{user_id}
- token_blacklist:{token}
- rate_limit:{ip}:{endpoint}

## Critical: All queries must filter by company_id for isolation!

## Next: Development Workflow (`07-development-workflow.md`)
