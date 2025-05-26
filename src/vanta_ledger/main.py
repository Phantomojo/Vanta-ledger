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
