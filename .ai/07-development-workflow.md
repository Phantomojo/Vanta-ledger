# 07 - Development Workflow

## Git Workflow
1. Create feature branch from main
2. Make changes with atomic commits
3. Write tests for new features
4. Run linters and tests locally
5. Create pull request
6. Code review required
7. Merge after approval

## Commit Messages
- Format: `type: description`
- Types: feat, fix, docs, refactor, test, chore
- Example: `feat: add document batch upload endpoint`

## Code Standards
- **Python**: Black formatter, Flake8 linter, mypy type checking
- **TypeScript**: ESLint, Prettier
- **Line Length**: 88 characters (Black default)
- **Type Hints**: Required for new Python code

## Pre-Commit Hooks (.pre-commit-config.yaml)
- detect-secrets (Yelp)
- bandit (security scanning)
- trufflehog (secret detection)
- black, isort, flake8, mypy
- yamllint, jsonlint, markdownlint

## Development Commands
```bash
# Backend
python -m uvicorn src.vanta_ledger.main:app --reload

# Frontend
cd frontend/frontend-web && npm run dev

# Tests
pytest tests/ -v

# Linting
black src/ && flake8 src/
```

## Next: Testing Strategy (`08-testing-strategy.md`)
