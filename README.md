# VantaLedger

VantaLedger is a lightweight FastAPI-based system for recording, retrieving, and analyzing transactions (sales and expenditures). Designed for both desktop and mobile usage, it simplifies financial data entry and reporting for small businesses or teams.

---

## 📂 Project Structure

```
src/vanta_ledger/
│
├── main.py                  # FastAPI app entry point
│
├── api/
│   └── endpoints.py         # All exposed REST API routes
│
├── core/
│   └── services.py          # Business logic (e.g., calculating totals)
│
├── crud.py                  # Handles direct DB operations
│
├── db/
│   ├── db.py                # DB engine config
│   ├── session.py           # Dependency-injected DB session (`get_db`)
│   └── base_class.py        # Shared SQLAlchemy base class
│
├── models/
│   ├── models.py            # Unified SQLAlchemy models (Expenditure, etc.)
│   └── transaction.py       # (To be merged into models.py for cleanup)
```

---

## 🔁 Flow Overview

1. **Client hits an endpoint** (like `POST /transactions`)
2. **FastAPI routes it** to the function in `api/endpoints.py`
3. **Endpoint depends on `get_db()`** from `db/session.py` to access the database
4. **The endpoint calls** either a function in `crud.py` (for DB I/O) or `services.py` (for business logic)
5. **Models from `models/models.py`** represent the database schema
6. **`db/db.py`** creates the DB engine (SQLite/PostgreSQL/etc.)

---

## 🧠 Key Concepts

| Component     | Role |
|---------------|------|
| `main.py`     | Launches FastAPI app and sets global routes & dependencies |
| `api/`        | Isolates endpoint logic (clean separation of concerns) |
| `core/`       | Contains services like calculations (e.g., `calculate_totals`) |
| `crud.py`     | Contains reusable DB operations |
| `models/`     | Defines the DB schema |
| `db/`         | Handles DB engine creation, session lifecycle, and base models |

---

## ✅ To Do

- [ ] Merge duplicate model definitions
- [ ] Implement missing business logic in `services.py`
- [ ] Write tests under `tests/` using `pytest`
- [ ] Add environment configuration using `.env`

---

## 👥 Contributors

- **Michael** – Backend lead, structure, and ops
- **Austin** – Python logic and business rules

---

## 💬 API Usage

Example:
```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"description": "New sale", "amount": 100, "type": "sale"}'
```

---

## 📦 Run Locally

```bash
# Run with uvicorn
uvicorn src.vanta_ledger.main:app --reload
```
```

---

Once you paste it, **press `CTRL + O`** then **Enter** to save, and **CTRL + X** to exit `nano`.

Want help merging those models or implementing the totals logic next?
