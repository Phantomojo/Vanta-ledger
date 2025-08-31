#!/usr/bin/env python3
"""
Security Fix Script for Vanta Ledger
Addresses critical security issues from audit
"""

import os
import re
from pathlib import Path

def fix_hardcoded_credentials():
    """Fix hardcoded credentials in backend files"""
    print("🔧 Fixing hardcoded credentials...")
    
    backend_path = Path("backend/src/vanta_ledger")
    
    # Find files with potential hardcoded credentials
    for py_file in backend_path.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace hardcoded patterns with environment variables
            patterns = [
                (r'password\s*=\s*["\'][^"\']+["\']', 'password = os.getenv("DB_PASSWORD", "")'),
                (r'secret\s*=\s*["\'][^"\']+["\']', 'secret = os.getenv("SECRET_KEY", "")'),
                (r'token\s*=\s*["\'][^"\']+["\']', 'token = os.getenv("API_TOKEN", "")'),
                (r'GITHUB_TOKEN\s*=\s*["\'][^"\']+["\']', 'GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")'),
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            # Add os import if needed
            if 'import os' not in content and 'from os import' not in content:
                content = 'import os\n' + content
            
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed: {py_file}")
                
        except Exception as e:
            print(f"❌ Error fixing {py_file}: {e}")

def create_secure_env_template():
    """Create secure environment template"""
    print("📝 Creating secure environment template...")
    
    template = '''# Vanta Ledger Environment Configuration
# Copy to .env and fill in secure values

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/vanta_ledger
MONGODB_URL=mongodb://localhost:27017/vanta_ledger
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-at-least-32-characters-long
JWT_SECRET_KEY=your-jwt-secret-key-at-least-32-characters-long

# API Keys
API_KEY=your-api-key-here
GITHUB_TOKEN=your-github-token-here

# Security Settings
DEBUG=False
ENABLE_HTTPS=True
ALLOWED_HOSTS=yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
'''
    
    with open(".env.template", "w") as f:
        f.write(template)
    
    print("✅ Created .env.template")

def main():
    """Main security fix function"""
    print("🔒 Vanta Ledger Security Fixes")
    print("=" * 40)
    
    fix_hardcoded_credentials()
    create_secure_env_template()
    
    print("\n✅ Security fixes completed!")
    print("📋 Next steps:")
    print("   1. Copy .env.template to .env")
    print("   2. Fill in secure environment variables")
    print("   3. Test the application")
    print("   4. Review security audit findings")

if __name__ == "__main__":
    main()
