#!/usr/bin/env python3
"""
PR Status Monitor for Vanta Ledger
Real-time monitoring of PR checks and status
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any

def run_gh_command(command: str) -> Dict[str, Any]:
    """Run a GitHub CLI command and return JSON result"""
    try:
        result = subprocess.run(
            f"gh {command}", 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: gh {command}")
        print(f"Error: {e.stderr}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON from: gh {command}")
        return {}

def analyze_pr_status(pr_number: int = 23) -> Dict[str, Any]:
    """Analyze PR status and return detailed report"""
    print(f"🔍 Analyzing PR #{pr_number} Status...")
    print("=" * 60)
    
    # Get PR details
    pr_data = run_gh_command(f"pr view {pr_number} --json statusCheckRollup,state,title,reviews")
    
    if not pr_data:
        return {"error": "Failed to fetch PR data"}
    
    # Analyze check statuses
    checks = pr_data.get("statusCheckRollup", [])
    
    # Categorize checks
    failed_checks = []
    successful_checks = []
    cancelled_checks = []
    skipped_checks = []
    in_progress_checks = []
    
    for check in checks:
        conclusion = check.get("conclusion", "")
        status = check.get("status", "")
        name = check.get("name", "")
        workflow = check.get("workflowName", "")
        
        check_info = {
            "name": name,
            "workflow": workflow,
            "conclusion": conclusion,
            "status": status,
            "details_url": check.get("detailsUrl", "")
        }
        
        if status == "IN_PROGRESS":
            in_progress_checks.append(check_info)
        elif conclusion == "FAILURE":
            failed_checks.append(check_info)
        elif conclusion == "SUCCESS":
            successful_checks.append(check_info)
        elif conclusion == "CANCELLED":
            cancelled_checks.append(check_info)
        elif conclusion == "SKIPPED":
            skipped_checks.append(check_info)
    
    # Generate summary
    summary = {
        "pr_number": pr_number,
        "title": pr_data.get("title", ""),
        "state": pr_data.get("state", ""),
        "total_checks": len(checks),
        "failed": len(failed_checks),
        "successful": len(successful_checks),
        "cancelled": len(cancelled_checks),
        "skipped": len(skipped_checks),
        "in_progress": len(in_progress_checks),
        "failed_checks": failed_checks,
        "successful_checks": successful_checks,
        "cancelled_checks": cancelled_checks,
        "skipped_checks": skipped_checks,
        "in_progress_checks": in_progress_checks
    }
    
    return summary

def print_status_report(summary: Dict[str, Any]):
    """Print a formatted status report"""
    print(f"📋 PR #{summary['pr_number']} Status Report")
    print(f"📝 Title: {summary['title']}")
    print(f"🔗 State: {summary['state']}")
    print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Overall status
    total = summary['total_checks']
    failed = summary['failed']
    successful = summary['successful']
    
    print("📊 Overall Status:")
    print(f"   Total Checks: {total}")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏸️  Cancelled: {summary['cancelled']}")
    print(f"   ⏭️  Skipped: {summary['skipped']}")
    print(f"   🔄 In Progress: {summary['in_progress']}")
    print()
    
    # Success rate
    if total > 0:
        success_rate = (successful / total) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 All checks are passing!")
        elif success_rate >= 80:
            print("⚠️  Most checks are passing, but some issues remain")
        else:
            print("🚨 Many checks are failing - immediate attention needed")
        print()
    
    # Failed checks details
    if summary['failed_checks']:
        print("❌ Failed Checks:")
        for check in summary['failed_checks']:
            print(f"   • {check['name']} ({check['workflow']})")
            if check['details_url']:
                print(f"     🔗 {check['details_url']}")
        print()
    
    # Successful checks
    if summary['successful_checks']:
        print("✅ Successful Checks:")
        workflows = {}
        for check in summary['successful_checks']:
            workflow = check['workflow']
            if workflow not in workflows:
                workflows[workflow] = []
            workflows[workflow].append(check['name'])
        
        for workflow, checks in workflows.items():
            print(f"   📁 {workflow}:")
            for check in checks:
                print(f"     • {check}")
        print()
    
    # Recommendations
    print("💡 Recommendations:")
    if failed > 0:
        print("   🔧 Fix the failing checks before merging")
        print("   📋 Review the failed check details for specific issues")
    else:
        print("   ✅ PR is ready for review and potential merge")
    
    if summary['in_progress'] > 0:
        print("   ⏳ Wait for in-progress checks to complete")
    
    print()

def get_detailed_failure_info(summary: Dict[str, Any]):
    """Get detailed information about failed checks"""
    if not summary['failed_checks']:
        return
    
    print("🔍 Detailed Failure Analysis:")
    print("=" * 60)
    
    for check in summary['failed_checks']:
        print(f"\n📋 {check['name']}")
        print(f"   Workflow: {check['workflow']}")
        print(f"   Status: {check['status']}")
        print(f"   Conclusion: {check['conclusion']}")
        
        # Try to get more details if available
        if check['details_url']:
            print(f"   🔗 Details: {check['details_url']}")
            
            # Extract run ID from URL for potential log access
            if "actions/runs/" in check['details_url']:
                run_id = check['details_url'].split("actions/runs/")[1].split("/")[0]
                print(f"   🆔 Run ID: {run_id}")
                print(f"   📝 To view logs: gh run view {run_id} --log-failed")

def main():
    """Main monitoring function"""
    print("🚀 Vanta Ledger PR Status Monitor")
    print("=" * 60)
    
    # Analyze PR status
    summary = analyze_pr_status(23)
    
    if "error" in summary:
        print(f"❌ {summary['error']}")
        return 1
    
    # Print status report
    print_status_report(summary)
    
    # Get detailed failure info
    get_detailed_failure_info(summary)
    
    # Final assessment
    print("🎯 Final Assessment:")
    if summary['failed'] == 0:
        print("   ✅ PR #23 is READY TO MERGE")
        print("   🎉 All checks are passing")
        return 0
    else:
        print("   ❌ PR #23 is NOT READY TO MERGE")
        print(f"   🔧 {summary['failed']} checks need to be fixed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
