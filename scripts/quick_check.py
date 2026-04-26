#!/usr/bin/env python3
"""
Quick progress check for Kaisper development
"""

import json
import subprocess
from datetime import datetime

def check_progress():
    """Check current progress."""
    # Load progress
    try:
        with open("/tmp/kaisper_progress.json", "r") as f:
            progress = json.load(f)
    except:
        return "No progress data available"
    
    # Check heartbeat log
    try:
        with open("/tmp/kaisper_heartbeat.log", "r") as f:
            log = f.readlines()
    except:
        log = []
    
    # Generate report
    report = f"""
📊 Kaisper Quick Progress Check
⏰ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project Status: {progress['status']}
Current Phase: {progress['current_phase']}
Agent ID: {progress['agent_id']}

Progress:
- Tasks: {progress['progress']['tasks_completed']}/{progress['progress']['tasks_total']}
- Code Lines: {progress['progress']['code_lines']}
- Tests: {progress['progress']['tests_passing']}/{progress['progress']['tests_total']}

Phases:
"""
    
    for phase in progress['phases']:
        status_emoji = "✅" if phase['status'] == "completed" else "🔄" if phase['status'] == "in_progress" else "⏳"
        report += f"{status_emoji} {phase['name']}: {phase['status']}\n"
    
    report += f"""
Recent Heartbeats:
"""
    
    for line in log[-5:]:
        report += f"  {line.strip()}\n"
    
    return report

if __name__ == "__main__":
    print(check_progress())
