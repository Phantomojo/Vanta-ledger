# 10 - Common Development Tasks

## Adding a New API Endpoint

1. Create route in `src/vanta_ledger/routes/<module>.py`:
```python
@router.post("/new-endpoint")
async def new_endpoint(data: InputModel):
    # Add company_id check for multi-tenant isolation!
    return {"status": "success"}
```

2. Define Pydantic models
3. Add business logic in services/
4. Write tests in tests/
5. Update API documentation

## Adding a Database Model

1. Create model in `src/vanta_ledger/models/`:
```python
class NewModel(Base):
    __tablename__ = "new_table"
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"))  # Required!
```

2. Create Pydantic schema
3. Add to database init
4. Create migration (Alembic)

## Adding a Service

1. Create file in `src/vanta_ledger/services/`
2. Implement business logic
3. Import in routes
4. Add tests

## Running Locally

```bash
# Quick test (no DB)
python -m uvicorn src.vanta_ledger.main_simple:app --reload

# With databases
docker-compose up -d postgres mongodb redis
python -m uvicorn src.vanta_ledger.main:app --reload
```

## Debugging

- Use FastAPI automatic docs: `/docs`
- Check logs: `logs/app.log`
- Database queries: SQLAlchemy echo=True
- Add print/logging statements
- Use Python debugger (pdb)

## Common Issues

**Import Error**: Check PYTHONPATH and virtual environment
**Database Connection**: Verify `.env` and services running
**Port In Use**: Change port or kill process
**Tests Failing**: Run individually to isolate issue

## Best Practices

✅ Always filter by company_id for multi-tenant isolation
✅ Validate input with Pydantic models
✅ Handle errors gracefully
✅ Write tests for new code
✅ Update documentation
✅ Follow existing patterns
✅ Use type hints
✅ Keep functions small and focused

## ✨ You're Ready!

You've completed the onboarding! You now understand:
- What Vanta Ledger is and its purpose
- System architecture and databases
- Code structure and organization
- Tech stack and tools
- API endpoints and data models
- Development workflow
- Testing approach
- Deployment options
- Common development tasks

## 🎯 Next Steps

Ask the developer: **"I've completed the AI onboarding for Vanta Ledger. What would you like me to help with?"**

Possible tasks:
- Add new features
- Fix bugs
- Improve performance
- Enhance security
- Write documentation
- Refactor code
- Add tests
- Review code

---

**Onboarding Complete!** 🎉
