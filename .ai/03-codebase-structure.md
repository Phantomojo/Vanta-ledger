# 03 - Codebase Structure

## Key Directories
- **src/vanta_ledger/** - Main application (routes, services, models)
- **frontend/frontend-web/** - React TypeScript UI
- **tests/** - Unit and integration tests
- **scripts/** - Setup, deployment, testing utilities
- **.ai/** - AI onboarding (this directory)
- **requirements/** - Modular dependencies (base/prod/dev/ai)

## Three Entry Points
1. `src/vanta_ledger/main.py` - Full production (all databases + AI)
2. `src/vanta_ledger/simple_main.py` - PostgreSQL only
3. `src/vanta_ledger/main_simple.py` - No databases (testing)

## Important Files
- `docker-compose.yml` - Full stack orchestration
- `pyproject.toml` - Python configuration (version 2.0.0)
- `.env.example` - Environment template
- `QUICK_START.md` - Setup guide
- `ENTRY_POINTS_GUIDE.md` - Entry point decisions

## Next: Tech Stack (`04-tech-stack.md`)
