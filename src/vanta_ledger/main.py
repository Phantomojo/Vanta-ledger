#!/usr/bin/env python3
"""
Main entry point for Vanta-ledger Enhanced application.

This module serves as the primary entry point for the application,
initializing the UI and backend components.
"""

import os
import sys
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import documents, ledger, paperless, projects, users, analytics, reports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vanta_ledger.log')
    ]
)
logger = logging.getLogger('vanta_ledger')

# Add parent directory to path to allow imports from frontend
parent_dir = str(Path(__file__).resolve().parent.parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import frontend components
try:
    from frontend.app import VantaLedgerApp
    from frontend.utils.auth import AuthManager
    from frontend.models.user import UserManager
    from frontend.models.owner import OwnerManager
    from frontend.models.transaction import TransactionManager
except ImportError as e:
    logger.error(f"Failed to import frontend components: {e}")
    print(f"Error: Failed to import frontend components: {e}")
    print("Please make sure you're running the application from the correct directory.")
    print("Use the launcher script (launch.py) for the best experience.")
    sys.exit(1)

app = FastAPI(title="Vanta Ledger API", description="Business Management and Intelligence Platform")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(ledger.router, prefix="/api/ledger", tags=["ledger"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(paperless.router, prefix="/api/paperless", tags=["paperless"])

# CORS: Allow React frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the projects router so the family can manage all projects in one place
app.include_router(projects.router)

# Include the documents router so the family can upload, organize, and version all important tender documents
app.include_router(documents.router)

# Include the ledger router so the family can track all income, expenses, and withdrawals for each project and company
app.include_router(ledger.router)

# Include the users router so the family can securely manage access and authentication
app.include_router(users.router)

# Include the paperless router
app.include_router(paperless.router)

# Include analytics and reports routers
app.include_router(analytics.router)
app.include_router(reports.router)

@app.get("/")
@app.get("/")
def read_root():
    return {"msg": "Vanta Ledger API is running", "version": "1.0.0"}

def main():
    """Main entry point for the application."""
    logger.info("Starting Vanta-ledger Enhanced")

    # Initialize managers
    auth_manager = AuthManager()
    user_manager = UserManager()
    owner_manager = OwnerManager()
    transaction_manager = TransactionManager()

    # Initialize and run the application
    app = VantaLedgerApp(
        auth_manager=auth_manager,
        user_manager=user_manager,
        owner_manager=owner_manager,
        transaction_manager=transaction_manager
    )

    try:
        app.run()
    except Exception as e:
        logger.error(f"Application crashed: {e}", exc_info=True)
        print(f"Error: Application crashed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    # Check if running as the main script
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        os.chdir(os.path.dirname(sys.executable))
    else:
        # Running as script
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Run the application
    sys.exit(main())