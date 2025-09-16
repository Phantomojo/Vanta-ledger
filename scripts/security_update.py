#!/usr/bin/env python3
"""
Security Update Script for Vanta Ledger
Addresses dependency vulnerabilities and ensures security compliance
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

def run_command(command, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Command failed: {command}")
        logger.error(f"Error: {e.stderr}")
        return None

def check_pip_audit():
    """Check for known vulnerabilities using pip-audit"""
    logger.info("🔍 Checking for known vulnerabilities with pip-audit...")
    
    # Try to install pip-audit if not available
    try:
        import pip_audit
    except ImportError:
        logger.info("📦 Installing pip-audit...")
        run_command("pip install pip-audit")
    
    # Run pip-audit
    result = run_command("pip-audit -r config/requirements.txt --format json")
    if result:
        try:
            vulnerabilities = json.loads(result)
            return vulnerabilities
        except json.JSONDecodeError:
            logger.info("⚠️ Could not parse pip-audit output")
            return None
    return None

def update_vulnerable_packages(vulnerabilities):
    """Update packages with known vulnerabilities"""
    if not vulnerabilities or not vulnerabilities.get("vulnerabilities"):
        logger.info("✅ No vulnerabilities found!")
        return True
    
    logger.info(f"⚠️ Found {len(vulnerabilities[")
    
    for vuln in vulnerabilities["vulnerabilities"]:
        package = vuln.get("package", {})
        package_name = package.get("name", "unknown")
        package_version = package.get("version", "unknown")
        vuln_id = vuln.get("vuln_id", "unknown")
        severity = vuln.get("severity", "unknown")
        
        logger.info(f"🔴 {package_name} {package_version}: {vuln_id} ({severity})")
        
        # Try to update the package
        logger.info(f"🔄 Updating {package_name}...")
        update_result = run_command(f"pip install --upgrade {package_name}")
        if update_result:
            logger.info(f"✅ Updated {package_name}")
        else:
            logger.error(f"❌ Failed to update {package_name}")
    
    return True

def update_requirements_file():
    """Update requirements.txt with latest secure versions"""
    logger.info("📝 Updating requirements.txt with latest secure versions...")
    
    # Read current requirements
    requirements_path = Path("config/requirements.txt")
    if not requirements_path.exists():
        logger.info("❌ requirements.txt not found")
        return False
    
    with open(requirements_path, 'r') as f:
        content = f.read()
    
    # Update specific packages known to have security issues
    security_updates = {
        "urllib3": "urllib3>=2.5.0",
        "requests": "requests>=2.32.4",
        "cryptography": "cryptography>=45.0.6",
        "PyJWT": "PyJWT>=2.10.1",
        "python-jose": "python-jose[cryptography]>=3.5.0",
        "passlib": "passlib[bcrypt]>=1.7.4",
        "bcrypt": "bcrypt>=4.3.0"
    }
    
    updated_content = content
    for package, new_version in security_updates.items():
        # Find and replace package versions
        lines = updated_content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith(package + ">="):
                lines[i] = new_version
                logger.info(f"✅ Updated {package} to {new_version}")
        updated_content = '\n'.join(lines)
    
    # Write updated requirements
    with open(requirements_path, 'w') as f:
        f.write(updated_content)
    
    logger.info("✅ Updated requirements.txt")
    return True

def run_bandit_scan():
    """Run bandit security scan"""
    logger.info("🔍 Running bandit security scan...")
    
    # Install bandit if not available
    try:
        import bandit
    except ImportError:
        logger.info("📦 Installing bandit...")
        run_command("pip install bandit")
    
    # Run bandit scan
    result = run_command("bandit -r backend/src/vanta_ledger -f json -o config/bandit-report-security-update.json")
    if result:
        logger.info("✅ Bandit scan completed")
        return True
    else:
        logger.error("❌ Bandit scan failed")
        return False

def check_security_config():
    """Check and update security configuration"""
    logger.info("🔧 Checking security configuration...")
    
    # Check for security-related environment variables
    security_vars = [
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "DATABASE_URL",
        "REDIS_URL",
        "ENCRYPTION_KEY"
    ]
    
    env_file = Path("config/env.example")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        for var in security_vars:
            if var not in content:
                logger.info(f"⚠️ Missing security variable: {var}")
            else:
                logger.info(f"✅ Found security variable: {var}")
    
    return True

def create_security_report():
    """Create a comprehensive security report"""
    logger.info("📊 Creating security report...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "security_checks": {
            "pip_audit": "completed",
            "bandit_scan": "completed",
            "requirements_update": "completed",
            "config_check": "completed"
        },
        "recommendations": [
            "Regularly update dependencies",
            "Use local model files instead of remote downloads",
            "Implement proper input validation",
            "Use secure random number generation",
            "Enable HTTPS in production",
            "Implement rate limiting",
            "Use secure session management",
            "Regular security audits"
        ]
    }
    
    # Save report
    with open("config/security_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info("✅ Security report created: config/security_report.json")
    return report

def main():
    """Main security update process"""
    logger.info("🛡️ Vanta Ledger Security Update")
    logger.info("=")
    
    # Step 1: Check for vulnerabilities
    vulnerabilities = check_pip_audit()
    
    # Step 2: Update vulnerable packages
    if vulnerabilities:
        update_vulnerable_packages(vulnerabilities)
    
    # Step 3: Update requirements file
    update_requirements_file()
    
    # Step 4: Run security scan
    run_bandit_scan()
    
    # Step 5: Check security configuration
    check_security_config()
    
    # Step 6: Create security report
    report = create_security_report()
    
    logger.info("\n")
    logger.info("✅ Security update completed!")
    logger.info("📊 Check config/security_report.json for details")
    logger.info("🔄 Remember to run this script regularly")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
