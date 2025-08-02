
#!/usr/bin/env python3
"""
Simple server runner for Replit environment
"""

import uvicorn
import os
from pathlib import Path
import sys

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set database URL - try PostgreSQL first, fallback to SQLite
database_url = os.getenv("DATABASE_URL")
if not database_url:
    # Try PostgreSQL if available
    if os.getenv("REPLIT_DB_URL"):
        database_url = os.getenv("REPLIT_DB_URL")
    else:
        # Fallback to SQLite
        database_url = "sqlite:///./vanta_ledger.db"
        
os.environ["DATABASE_URL"] = database_url

if __name__ == "__main__":
    try:
        from vanta_ledger.main import app
        print("🚀 Starting Vanta Ledger API server...")
        print("📊 Access API docs at: http://0.0.0.0:5000/docs")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=5000,
            reload=False,  # Disable reload in Replit
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: python setup_database.py first")
    except Exception as e:
        print(f"❌ Server error: {e}")
