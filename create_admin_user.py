#!/usr/bin/env python3
"""
Create admin user for Vanta Ledger
"""

import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from vanta_ledger.services.user_service import get_user_service
from vanta_ledger.models.user_models import UserCreate

def create_admin_user():
    """Create admin user"""
    try:
        user_service = get_user_service()
        
        # Create admin user
        admin_data = UserCreate(
            username="admin",
            email="admin@vanta.com",
            password="Admin123!",
            role="admin"
        )
        
        user = user_service.create_user(admin_data)
        print(f"✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Email: admin@vanta.com")
        print(f"   Password: Admin123!")
        print(f"   Role: admin")
        
        return user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return None

if __name__ == "__main__":
    create_admin_user() 