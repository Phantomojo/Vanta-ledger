#!/usr/bin/env python3
"""
GitHub Token Setup Script for Vanta Ledger
Helps users set up their GitHub token for the GitHub Models Service
"""

import os
import sys
from pathlib import Path

def check_github_cli():
    """Check if GitHub CLI is available"""
    try:
        import subprocess
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_token_from_gh():
    """Get token from GitHub CLI"""
    try:
        import subprocess
        result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"Error getting token from GitHub CLI: {e}")
        return None

def setup_env_file():
    """Set up .env file with GitHub token"""
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if not env_file.exists():
        if env_template.exists():
            print("📝 Creating .env file from template...")
            with open(env_template, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
        else:
            print("📝 Creating new .env file...")
            with open(env_file, 'w') as f:
                f.write("# Vanta Ledger Environment Configuration\n")
                f.write("# Copy to .env and fill in secure values\n\n")
                f.write("# Database\n")
                f.write("DATABASE_URL=postgresql://username:password@localhost:5432/vanta_ledger\n")
                f.write("MONGODB_URL=mongodb://localhost:27017/vanta_ledger\n")
                f.write("REDIS_URL=redis://localhost:6379/0\n\n")
                f.write("# Security\n")
                f.write("SECRET_KEY=your-super-secret-key-at-least-32-characters-long\n")
                f.write("JWT_SECRET_KEY=your-jwt-secret-key-at-least-32-characters-long\n\n")
                f.write("# API Keys\n")
                f.write("API_KEY=your-api-key-here\n")
                f.write("GITHUB_TOKEN=your-github-token-here\n\n")
                f.write("# Security Settings\n")
                f.write("DEBUG=False\n")
                f.write("ENABLE_HTTPS=True\n")
                f.write("ALLOWED_HOSTS=yourdomain.com\n")
                f.write("CORS_ORIGINS=https://yourdomain.com\n\n")
                f.write("# Rate Limiting\n")
                f.write("RATE_LIMIT_REQUESTS=100\n")
                f.write("RATE_LIMIT_WINDOW=3600\n")
    
    return env_file

def update_env_file(env_file, token):
    """Update .env file with GitHub token"""
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check if GITHUB_TOKEN already exists
        if "GITHUB_TOKEN=" in content:
            # Update existing token
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("GITHUB_TOKEN="):
                    lines[i] = f"GITHUB_TOKEN={token}"
                    break
            
            content = '\n'.join(lines)
        else:
            # Add new token
            content += f"\n# GitHub Models\nGITHUB_TOKEN={token}\n"
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {env_file} with GitHub token")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def test_github_models():
    """Test GitHub Models service"""
    try:
        # Add the backend to Python path
        backend_path = Path("backend/src")
        if backend_path.exists():
            sys.path.insert(0, str(backend_path))
        
        from vanta_ledger.services.github_models_service import GitHubModelsService
        
        service = GitHubModelsService()
        
        print(f"🔧 GitHub Models Service Status:")
        print(f"   Enabled: {service.enabled}")
        print(f"   Token Available: {bool(service.token)}")
        print(f"   Default Model: {service.default_model}")
        
        if service.enabled:
            print("✅ GitHub Models Service is ready!")
            return True
        else:
            print("❌ GitHub Models Service is not enabled")
            return False
            
    except ImportError as e:
        print(f"❌ Error importing GitHub Models Service: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing GitHub Models Service: {e}")
        return False

def main():
    """Main setup function"""
    print("🔑 GitHub Token Setup for Vanta Ledger")
    print("=" * 50)
    
    # Check if GitHub CLI is available
    if check_github_cli():
        print("🖥️ GitHub CLI detected!")
        
        # Try to get token from GitHub CLI
        token = get_token_from_gh()
        if token:
            print("✅ Retrieved token from GitHub CLI")
        else:
            print("⚠️ Could not get token from GitHub CLI")
            token = None
    else:
        print("⚠️ GitHub CLI not found")
        token = None
    
    # If no token from CLI, ask user
    if not token:
        print("\n📝 Manual Token Setup:")
        print("1. Go to GitHub.com → Settings → Developer settings → Personal access tokens")
        print("2. Generate a new token with 'repo' permissions")
        print("3. Copy the token and paste it below")
        print()
        
        token = input("Enter your GitHub token: ").strip()
        
        if not token:
            print("❌ No token provided. Setup cancelled.")
            return
    
    # Set up .env file
    env_file = setup_env_file()
    
    # Update .env file with token
    if update_env_file(env_file, token):
        print(f"✅ Token saved to {env_file}")
    else:
        print("❌ Failed to save token")
        return
    
    # Test the setup
    print("\n🧪 Testing GitHub Models Service...")
    if test_github_models():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the service: python scripts/test_core_models.py")
        print("2. Start the application: python -m vanta_ledger.main")
        print("3. Access GitHub Models API at: /github-models/health")
    else:
        print("\n❌ Setup completed but service test failed")
        print("Please check your token and try again")

if __name__ == "__main__":
    main()
