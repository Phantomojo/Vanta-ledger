# Scripts Directory

This directory contains utility scripts organized by purpose.

## Directory Structure

```
scripts/
├── setup/          - Initial setup and configuration scripts
├── database/       - Database management and migration scripts
├── deployment/     - Application deployment and startup scripts
├── testing/        - Testing, monitoring, and health check scripts
└── [other]/        - Additional utility scripts
```

## Script Categories

### 📦 Setup Scripts (`setup/`)
Scripts for initial project setup, user creation, and system configuration:
- `create_admin_user.py` - Create admin user accounts
- `create_secure_admin.py` - Create secure admin with enhanced security
- `setup_initial_data.py` - Initialize database with sample data
- `setup_hybrid_system.py` - Configure hybrid database system
- `create_initial_admin.py` - Create first admin user
- `setup_project.py` - Complete project setup
- `generate_env.py` - Generate environment configuration
- `generate_mock_data.py` - Generate mock data for testing

### 🗄️ Database Scripts (`database/`)
Scripts for database operations:
- `backup_and_migrate.py` - Database backup and migration utilities
- `init_database.py` - Initialize database schema

### 🚀 Deployment Scripts (`deployment/`)
Scripts for starting and managing the application:
- `launch_vanta_ledger.py` - Main application launcher
- `start_backend.py` - Start backend server
- `start_local_llm.py` - Start local LLM service

### 🧪 Testing Scripts (`testing/`)
Scripts for testing, monitoring, and system checks:
- `check_status.py` - Check application status
- `check_system_health.py` - System health monitoring
- `run_comprehensive_tests.py` - Run full test suite
- `demo_github_models_capabilities.py` - Demo GitHub models integration
- `updatedps.py` - Update dependencies

### 📝 Other Scripts
Additional utility scripts:
- `analyze_documents.py` - Document analysis tools
- `download_llm_models.py` - Download LLM models

## Usage

### Running Setup Scripts
```bash
# Create admin user
python scripts/setup/create_admin_user.py

# Initialize database
python scripts/database/init_database.py

# Setup complete system
python scripts/setup/setup_hybrid_system.py
```

### Starting the Application
```bash
# Start complete application
python scripts/deployment/launch_vanta_ledger.py

# Start only backend
python scripts/deployment/start_backend.py
```

### Testing and Monitoring
```bash
# Check system health
python scripts/testing/check_system_health.py

# Run comprehensive tests
python scripts/testing/run_comprehensive_tests.py
```

## Adding New Scripts

When adding new scripts:
1. Place them in the appropriate subdirectory
2. Add a docstring at the top explaining purpose
3. Include usage examples in comments
4. Update this README with the new script info

## Script Naming Convention

- Use lowercase with underscores: `script_name.py`
- Start with verb: `create_`, `setup_`, `check_`, `run_`, etc.
- Be descriptive: Clearly indicate what the script does

## Environment Requirements

Most scripts require:
- Python 3.8+
- Virtual environment activated
- Environment variables configured (see `.env.example`)
- Database services running (for database scripts)

## Troubleshooting

If a script fails:
1. Check that virtual environment is activated
2. Verify environment variables are set (`.env` file)
3. Ensure database services are running
4. Check script's docstring for specific requirements
5. Review error messages for missing dependencies

For more help, see main README.md or open an issue.
