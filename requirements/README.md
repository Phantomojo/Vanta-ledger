# Requirements Directory

This directory contains organized dependency files for different installation scenarios.

## Files

- **`base.txt`** - Core dependencies required for all installations
- **`prod.txt`** - Production dependencies (includes base)
- **`dev.txt`** - Development dependencies (includes prod)
- **`ai.txt`** - AI/ML dependencies (optional, large packages)

## Installation

### For Production
```bash
pip install -r requirements/prod.txt -c constraints.txt
```

### For Development
```bash
pip install -r requirements/dev.txt
```

### With AI Features
```bash
pip install -r requirements/ai.txt -c constraints.txt
```

### Minimal Installation (Base Only)
```bash
pip install -r requirements/base.txt -c constraints.txt
```

## Dependency Structure

```
dev.txt
 └── prod.txt
      └── base.txt

ai.txt
 └── base.txt
```

## Legacy Files

The root-level `requirements.txt` and `constraints.txt` are maintained for backward compatibility but the new requirements/ structure is recommended for new installations.

## Version Pinning

Use `constraints.txt` in the root directory for exact version pinning in production:

```bash
pip install -r requirements/prod.txt -c constraints.txt
```

## Updating Dependencies

To update dependencies:

1. Update the appropriate file in requirements/
2. Test the changes
3. Update constraints.txt with exact versions if needed
4. Run security scan: `safety check`

## Package Categories

### Base
- FastAPI and web framework
- Database drivers
- Authentication
- Basic utilities

### Production
- Document processing
- Production logging
- Monitoring
- Data processing

### Development
- Testing frameworks
- Linting and formatting
- Security scanning
- Documentation tools

### AI
- Machine learning frameworks
- NLP libraries
- LLM integration
- Data science tools
