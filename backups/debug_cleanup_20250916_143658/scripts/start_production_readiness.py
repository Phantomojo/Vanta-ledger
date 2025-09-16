#!/usr/bin/env python3
"""
Vanta Ledger - Production Readiness Starter Script

This script helps kickstart the production readiness process by:
1. Diagnosing current issues
2. Setting up the development environment
3. Running initial assessments
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class ProductionReadinessStarter:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.start_time = datetime.now()
        self.results = {
            "timestamp": self.start_time.isoformat(),
            "issues_found": [],
            "recommendations": [],
            "next_steps": []
        }
    
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, command, description):
        """Run a command and capture results"""
        self.log(f"Running: {description}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            if result.returncode == 0:
                self.log(f"✅ {description} - SUCCESS")
                return result.stdout
            else:
                self.log(f"❌ {description} - FAILED: {result.stderr}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ {description} - ERROR: {str(e)}", "ERROR")
            return None
    
    def check_python_environment(self):
        """Check Python environment and dependencies"""
        self.log("🔍 Checking Python environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 8:
            self.log(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            self.results["issues_found"].append({
                "type": "python_version",
                "severity": "critical",
                "message": f"Python {python_version.major}.{python_version.minor} is not supported. Need Python 3.8+"
            })
        
        # Check if virtual environment is active
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.log("✅ Virtual environment is active")
        else:
            self.results["issues_found"].append({
                "type": "virtual_env",
                "severity": "warning",
                "message": "No virtual environment detected. Recommended to use venv."
            })
    
    def check_test_infrastructure(self):
        """Check testing infrastructure"""
        self.log("🔍 Checking test infrastructure...")
        
        # Check if pytest is installed
        pytest_result = self.run_command("python -m pytest --version", "Check pytest installation")
        if not pytest_result:
            self.results["issues_found"].append({
                "type": "pytest_missing",
                "severity": "critical",
                "message": "pytest is not installed or not working"
            })
            self.results["recommendations"].append("Install pytest: pip install pytest pytest-asyncio")
        
        # Try to discover tests
        test_discovery = self.run_command("python -m pytest --collect-only -q", "Test discovery")
        if test_discovery:
            test_count = len([line for line in test_discovery.split('\n') if 'test session starts' in line])
            if test_count > 0:
                self.log(f"✅ Found {test_count} test sessions")
            else:
                self.results["issues_found"].append({
                    "type": "no_tests_found",
                    "severity": "critical",
                    "message": "No tests discovered by pytest"
                })
        else:
            self.results["issues_found"].append({
                "type": "test_discovery_failed",
                "severity": "critical",
                "message": "Test discovery failed"
            })
    
    def check_debug_code(self):
        """Check for debug code (print statements)"""
        self.log("🔍 Checking for debug code...")
        
        # Find files with print statements
        result = self.run_command(
            'find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -exec grep -l "print(" {} \; | wc -l',
            "Count files with print statements"
        )
        
        if result:
            print_count = int(result.strip())
            if print_count > 0:
                self.results["issues_found"].append({
                    "type": "debug_code",
                    "severity": "high",
                    "message": f"Found {print_count} files with print() statements"
                })
                self.results["recommendations"].append("Replace print() statements with proper logging")
            else:
                self.log("✅ No print statements found")
    
    def check_security_issues(self):
        """Check for security issues"""
        self.log("🔍 Checking for security issues...")
        
        # Check if bandit is available
        bandit_result = self.run_command("bandit --version", "Check bandit installation")
        if bandit_result:
            # Run security scan
            security_scan = self.run_command(
                "bandit -r backend/src/ -f json",
                "Run security scan"
            )
            if security_scan:
                try:
                    security_data = json.loads(security_scan)
                    high_issues = security_data.get("results", [])
                    if high_issues:
                        self.results["issues_found"].append({
                            "type": "security_issues",
                            "severity": "high",
                            "message": f"Found {len(high_issues)} security issues"
                        })
                    else:
                        self.log("✅ No critical security issues found")
                except json.JSONDecodeError:
                    self.log("⚠️ Could not parse security scan results", "WARNING")
        else:
            self.results["recommendations"].append("Install bandit for security scanning: pip install bandit")
    
    def check_dependencies(self):
        """Check dependency issues"""
        self.log("🔍 Checking dependencies...")
        
        # Count dependencies
        if (self.project_root / "config" / "requirements.txt").exists():
            with open(self.project_root / "config" / "requirements.txt", 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                dep_count = len(lines)
                
                if dep_count > 150:
                    self.results["issues_found"].append({
                        "type": "too_many_dependencies",
                        "severity": "medium",
                        "message": f"Found {dep_count} dependencies - consider reducing"
                    })
                else:
                    self.log(f"✅ Dependency count: {dep_count}")
    
    def generate_report(self):
        """Generate a summary report"""
        self.log("📊 Generating report...")
        
        report = f"""
# Vanta Ledger - Production Readiness Assessment

**Assessment Date:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {(datetime.now() - self.start_time).total_seconds():.1f} seconds

## 🚨 Critical Issues Found: {len([i for i in self.results['issues_found'] if i['severity'] == 'critical'])}

"""
        
        for issue in self.results["issues_found"]:
            severity_emoji = {"critical": "🔴", "high": "🟡", "medium": "🟢", "low": "🔵"}.get(issue["severity"], "⚪")
            report += f"- {severity_emoji} **{issue['type']}**: {issue['message']}\n"
        
        report += f"""
## 💡 Recommendations: {len(self.results['recommendations'])}

"""
        
        for rec in self.results["recommendations"]:
            report += f"- {rec}\n"
        
        report += f"""
## 🎯 Next Steps

1. **Immediate Actions:**
   - Fix critical issues first
   - Set up proper testing environment
   - Remove debug code

2. **This Week:**
   - Complete Phase 1 tasks
   - Set up CI/CD pipeline
   - Implement proper logging

3. **Next Week:**
   - Optimize dependencies
   - Harden Docker configuration
   - Complete integration testing

## 📋 Full Results

```json
{json.dumps(self.results, indent=2)}
```
"""
        
        # Save report
        report_file = self.project_root / "PRODUCTION_READINESS_ASSESSMENT.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        self.log(f"📄 Report saved to: {report_file}")
        print("\n" + "="*60)
        print(report)
        print("="*60)
    
    def run_assessment(self):
        """Run the complete assessment"""
        self.log("🚀 Starting Vanta Ledger Production Readiness Assessment")
        self.log("="*60)
        
        # Run all checks
        self.check_python_environment()
        self.check_test_infrastructure()
        self.check_debug_code()
        self.check_security_issues()
        self.check_dependencies()
        
        # Generate report
        self.generate_report()
        
        self.log("✅ Assessment complete!")
        self.log("📋 Check PRODUCTION_READINESS_ASSESSMENT.md for detailed results")
        self.log("📋 Check PRODUCTION_READINESS_PLAN.md for action plan")
        self.log("📋 Check PROGRESS_TRACKER.md for progress tracking")

if __name__ == "__main__":
    starter = ProductionReadinessStarter()
    starter.run_assessment()
