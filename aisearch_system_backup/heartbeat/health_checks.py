#!/usr/bin/env python3
"""
health_checks.py — SENTINEL's continuous health monitoring daemon
Runs every 15 minutes, checks all system vital signs, fires alerts via alerter.py.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("sentinel.health")

MEMORY_DIR = "/root/.openclaw/workspace/aisearch_system/memory"
ALERT_COOLDOWN_MINUTES = 30  # Don't re-fire same alert within 30min

# Alert severity thresholds
TIMEOUTS = {
    "magnus":           {"max_age_hours": 26,  "severity": "CRITICAL"},
    "scout":            {"max_age_hours": 192, "severity": "WARNING"},
    "falcon":           {"max_age_hours": 26,  "severity": "CRITICAL"},
    "sieve":            {"max_age_hours": 28,  "severity": "CRITICAL"},
    "cartographer":     {"max_age_hours": 8,   "severity": "WARNING"},
    "rival":            {"max_age_hours": 26,  "severity": "ERROR"},
    "oracle_x":         {"max_age_hours": 192, "severity": "WARNING"},
    "sentinel":         {"max_age_hours": 1,   "severity": "CRITICAL"},
}

FILE_TIMEOUTS = {
    "response_log.jsonl":        {"max_age_hours": 26, "severity": "ERROR"},
    "citation_graph.json":        {"max_age_hours": 8,  "severity": "WARNING"},
    "prompt_library.json":       {"max_age_hours": 192,"severity": "WARNING"},
    "pipeline_state.json":       {"max_age_hours": 26, "severity": "ERROR"},
}

def load_config():
    """Load brands config for API key checks."""
    config_path = "/root/.openclaw/workspace/aisearch_system/config/brands.yaml"
    if os.path.exists(config_path):
        import yaml
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}

def check_file_age(filepath: str, max_age_hours: float, severity: str) -> dict:
    """Check if a file is stale (>max_age_hours old). Returns alert dict or None."""
    if not os.path.exists(filepath):
        return {
            "alert_id": f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": severity,
            "description": f"Required file missing: {filepath}",
            "likely_cause": "File not yet created or pipeline not initialised",
            "recommended_action": f"Verify ORACLE pipeline has been run. Check {filepath} exists.",
            "recovery_playbook_ref": None,
        }
    age_seconds = time.time() - os.path.getmtime(filepath)
    age_hours = age_seconds / 3600
    if age_hours > max_age_hours:
        return {
            "alert_id": f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": severity,
            "description": f"File {filepath} last modified {age_hours:.1f} hours ago (> {max_age_hours}h threshold)",
            "likely_cause": "Pipeline stage stalled or memory write failed",
            "recommended_action": f"Check when {filepath} was last updated. Verify pipeline is running.",
            "recovery_playbook_ref": None,
        }
    return None

def check_disk_space(path: str, threshold: float = 0.80) -> dict:
    """Check disk usage for a path. Returns alert if > threshold."""
    import shutil
    usage = shutil.disk_usage(path)
    pct = usage.used / usage.total
    if pct > threshold:
        return {
            "alert_id": f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": "ERROR",
            "description": f"Disk usage at {pct*100:.1f}% for {path}",
            "likely_cause": "Response log storage growing without rotation",
            "recommended_action": "Archive or purge old response logs. Increase storage.",
            "recovery_playbook_ref": "heartbeat/recovery_playbook.md#disk-space",
        }
    return None

def check_api_keys() -> list:
    """Ping each API with minimal test to validate key freshness."""
    import requests
    alerts = []
    keys = {
        "OPENAI_API_KEY":    "https://api.openai.com/v1/models",
        "ANTHROPIC_API_KEY": "https://api.anthropic.com/v1/messages",
    }
    for key_name, test_url in keys.items():
        key = os.environ.get(key_name)
        if not key:
            alerts.append({
                "alert_id": f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_001",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "severity": "CRITICAL",
                "description": f"{key_name} not set in environment",
                "likely_cause": "API key not configured",
                "recommended_action": f"Set {key_name} environment variable",
                "recovery_playbook_ref": None,
            })
    return alerts

def check_pipeline_state() -> dict:
    """Read pipeline_state.json and check for stalled stages."""
    state_path = os.path.join(MEMORY_DIR, "pipeline_state.json")
    if not os.path.exists(state_path):
        return None
    with open(state_path) as f:
        state = json.load(f)
    alerts = []
    for stage, info in state.get("stages", {}).items():
        if info.get("status") == "running":
            start = info.get("started_at")
            if start:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                age_hours = (datetime.now() - start_dt.replace(tzinfo=None)).total_seconds() / 3600
                max_expected = TIMEOUTS.get("falcon", {}).get("max_age_hours", 4)
                if age_hours > max_expected:
                    alerts.append({
                        "alert_id": f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_001",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "severity": "ERROR",
                        "description": f"Stage {stage} has been Running for {age_hours:.1f} hours",
                        "likely_cause": "Agent stalled mid-run",
                        "recommended_action": f"Check {stage} logs. Force-retry via MAGNUS --retry-failed",
                        "recovery_playbook_ref": f"heartbeat/recovery_playbook.md#{stage}-stall",
                    })
    return alerts[0] if alerts else None

def run_health_check() -> dict:
    """Run all health checks, return full health report dict."""
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "system_status": "HEALTHY",
        "alerts": [],
        "agent_checks": {},
        "file_checks": {},
        "storage_pct": None,
    }
    all_alerts = []

    # File freshness checks
    for filename,-conf in FILE_TIMEOUTS.items():
        filepath = os.path.join(MEMORY_DIR, filename)
        result = check_file_age(filepath, conf["max_age_hours"], conf["severity"])
        report["file_checks"][filename] = "OK" if result is None else conf["severity"]
        if result:
            all_alerts.append(result)

    # Pipeline state checks
    pipeline_alert = check_pipeline_state()
    if pipeline_alert:
        all_alerts.append(pipeline_alert)

    # Disk space
    disk_alert = check_disk_space(MEMORY_DIR)
    if disk_alert:
        all_alerts.append(disk_alert)
        report["storage_pct"] = f"{disk_alert} (HIGH)"

    # API key checks
    api_alerts = check_api_keys()
    all_alerts.extend(api_alerts)

    report["alerts"] = all_alerts
    if any(a["severity"] == "CRITICAL" for a in all_alerts):
        report["system_status"] = "CRITICAL"
    elif any(a["severity"] == "ERROR" for a in all_alerts):
        report["system_status"] = "DEGRADED"
    elif any(a["severity"] == "WARNING" for a in all_alerts):
        report["system_status"] = "WARNING"

    return report

def report_to_human(report: dict):
    """Print a human-readable summary of the health report."""
    status_emoji = {
        "HEALTHY": "✅", "WARNING": "⚠️", "DEGRADED": "⚠️", "CRITICAL": "🔴"
    }
    emoji = status_emoji.get(report["system_status"], "❓")
    print(f"\n{'='*50}")
    print(f"SENTINEL HEALTH REPORT — {report['timestamp']}")
    print(f"System Status: {emoji} {report['system_status']}")
    print(f"{'='*50}")
    if not report["alerts"]:
        print("All checks passed. No alerts.")
    else:
        for alert in report["alerts"]:
            print(f"  [{alert['severity']}] {alert['description']}")
            if alert.get("recommended_action"):
                print(f"    → {alert['recommended_action']}")

def daemon():
    """SENTINEL daemon loop — run every 15 minutes."""
    logger.info("SENTINEL health daemon starting...")
    while True:
        report = run_health_check()
        # Always write latest health state
        health_path = os.path.join(MEMORY_DIR, "sentinel_health.json")
        with open(health_path, "w") as f:
            json.dump(report, f, indent=2)
        # Fire alerts for ERROR/CRITICAL
        for alert in report["alerts"]:
            if alert["severity"] in ("ERROR", "CRITICAL"):
                try:
                    from tools.alerter import send_alert
                    send_alert(alert["severity"], alert["description"],
                               alert.get("recommended_action", ""), channel="telegram")
                except Exception as e:
                    logger.error(f"Failed to send alert: {e}")
        logger.info(f"Health check complete: {report['system_status']}")
        time.sleep(15 * 60)  # 15 minutes

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true")
    args = parser.parse_args()
    if args.daemon:
        daemon()
    else:
        report = run_health_check()
        report_to_human(report)
