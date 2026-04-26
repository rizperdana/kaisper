#!/usr/bin/env python3
"""
Kaisper Heartbeat - Autonomous Progress Monitoring

This script runs every 30 minutes via cron to:
- Check ClawTeam status
- Review agent outputs
- Run tests
- Verify requirements
- Make autonomous decisions
- Report progress to user
"""

import subprocess
import json
import os
from datetime import datetime

PROJECT_DIR = "/home/anon/Projects/experiment/kaisper"
LOG_FILE = "/tmp/kaisper_heartbeat.log"
REPORT_FILE = "/tmp/kaisper_heartbeat_report.txt"

def log(message):
    """Log message to file."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")

def check_clawteam_status():
    """Check ClawTeam team status."""
    try:
        result = subprocess.run(
            ["clawteam", "team", "status", "kaisper"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.returncode == 0
    except Exception as e:
        return f"Error: {str(e)}", False

def check_task_progress():
    """Check task progress."""
    try:
        result = subprocess.run(
            ["clawteam", "task", "list", "kaisper"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.returncode == 0
    except Exception as e:
        return f"Error: {str(e)}", False

def run_tests():
    """Run tests and check results."""
    try:
        result = subprocess.run(
            ["pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=PROJECT_DIR
        )
        return result.stdout, result.returncode == 0
    except Exception as e:
        return f"Error: {str(e)}", False

def review_code_quality():
    """Review code quality."""
    try:
        # Check for TODO/FIXME comments
        result = subprocess.run(
            ["grep", "-r", "TODO|FIXME", "src/"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
        todos = result.stdout if result.returncode == 0 else "None"
        
        # Check code style
        result = subprocess.run(
            ["ruff", "check", "src/"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
        style_issues = result.stdout if result.returncode != 0 else "None"
        
        return f"TODOs: {todos}\nStyle Issues: {style_issues}", True
    except Exception as e:
        return f"Error: {str(e)}", False

def verify_requirements():
    """Verify requirements are met."""
    checks = []
    
    # Check if PostgreSQL is running
    try:
        subprocess.run(
            ["pg_isready"],
            capture_output=True,
            timeout=5
        )
        checks.append("✅ PostgreSQL: Running")
    except:
        checks.append("❌ PostgreSQL: Not running")
    
    # Check if Obscura is available
    try:
        subprocess.run(
            ["obscura", "--version"],
            capture_output=True,
            timeout=5
        )
        checks.append("✅ Obscura: Available")
    except:
        checks.append("❌ Obscura: Not available")
    
    # Check if project structure exists
    if os.path.exists(f"{PROJECT_DIR}/src/kaisper"):
        checks.append("✅ Project structure: OK")
    else:
        checks.append("❌ Project structure: Missing")
    
    return "\n".join(checks), True

def make_decision(status, progress, tests, quality, requirements):
    """Make autonomous decision based on checks."""
    decisions = []
    
    # Check if team is active
    if "Active" not in status:
        decisions.append("⚠️ Team not active - may need intervention")
    
    # Check if tests are passing
    if not tests[1]:
        decisions.append("⚠️ Tests failing - review needed")
    
    # Check if requirements met
    if "❌" in requirements[0]:
        decisions.append("⚠️ Requirements not met - fix needed")
    
    # Check if there are many TODOs
    if "TODO" in quality[0] and quality[0].count("TODO") > 5:
        decisions.append("⚠️ Many TODOs - review needed")
    
    if not decisions:
        decisions.append("✅ All checks passing - continue")
    
    return "\n".join(decisions)

def generate_report():
    """Generate comprehensive progress report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log("Starting heartbeat check")
    
    # Run all checks
    status, status_ok = check_clawteam_status()
    progress, progress_ok = check_task_progress()
    tests, tests_ok = run_tests()
    quality, quality_ok = review_code_quality()
    requirements, req_ok = verify_requirements()
    decisions = make_decision(status, progress, (tests, tests_ok), (quality, quality_ok), (requirements, req_ok))
    
    # Generate report
    report = f"""
🤖 Kaisper Heartbeat Report
⏰ {timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Team Status:
{status}

📋 Task Progress:
{progress}

🧪 Test Results:
{tests}

📝 Code Quality:
{quality}

✅ Requirements Check:
{requirements}

🎯 Autonomous Decision:
{decisions}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Action: Continue monitoring
Next Heartbeat: 30 minutes
"""
    
    log("Heartbeat check complete")
    return report

def send_report(report):
    """Send report to user."""
    # Write to file
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    
    log("Report saved to file")
    
    # Note: The message tool will be called by the cron job
    return REPORT_FILE

def main():
    """Main heartbeat function."""
    try:
        log("=== Heartbeat Started ===")
        
        # Generate report
        report = generate_report()
        
        # Send report
        report_file = send_report(report)
        
        log(f"Report generated: {report_file}")
        log("=== Heartbeat Complete ===")
        
        return 0
    except Exception as e:
        error_msg = f"❌ Heartbeat Error: {str(e)}"
        log(error_msg)
        
        # Write error report
        with open(REPORT_FILE, "w") as f:
            f.write(error_msg)
        
        return 1

if __name__ == "__main__":
    exit(main())
