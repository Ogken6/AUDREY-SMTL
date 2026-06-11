#!/usr/bin/env python3
"""
sentinel.py — ORACLE System Health & Heartbeat Monitor
Runs as a daemon process, independent of MAGNUS.
Checks all system components on a configurable interval.
Alerts via Slack, email, and SMS based on severity.
Usage:
    python agents/sentinel.py --daemon --brand=crispyglaze
    python agents/sentinel.py --check-now
    python agents/sentinel.py --test-alert
"""

import os
import sys
import json
import time
import socket
import argparse
import logging
import threading
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.alerter import Alerter
from tools.db_writer import DBWriter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "logs" / "sentinel.log"),
    ],
)
logger = logging.getLogger("sentinel")

HEALTH_STATE_PATH = PROJECT_ROOT / "memory" / "sentinel_health.json"
CONFIG_PATH = PROJECT_ROOT / "config" / "thresholds.yaml"
AGENT_HEARTBEAT_PATH = PROJECT_ROOT / "memory" / "agent_heartbeat.json"

CHECK_INTERVAL_SECONDS = 300  # 5 minutes default

ALERT_COOLDOWN = {
    "INFO": 3600,     # 1 hour between INFO alerts
    "WARNING": 1800, # 30 min between WARNING alerts
    "ERROR": 300,     # 5 min between ERROR alerts
    "CRITICAL": 60,   # 1 min between CRITICAL alerts
}

class Sentinel:
    """
    SENTINEL is ORACLE's system health monitor.
    It runs as a separate OS process — MAGNUS cannot suppress SENTINEL alerts.
    SENTINEL does not make decisions about pipeline health — it only alerts.
    Interpretation is left to the human operator.
    """

    def __init__(self, brand: str, check_interval: int = CHECK_INTERVAL_SECONDS):
        self.brand = brand
        self.check_interval = check_interval
        self.alerter = Alerter()
        self.db = DBWriter()
        self.thresholds = self._load_thresholds()
        self.health_state = self._load_health_state()
        self.last_alert_times = defaultdict(int)  # severity -> timestamp
        self.running = False

    def _load_thresholds(self) -> dict:
        import yaml
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH) as f:
                return yaml.safe_load(f).get("thresholds", {})
        return {
            "pipeline_max_duration_minutes": 240,
            "extraction_confidence_min": 0.70,
            "error_rate_max_percent": 20,
            "api_latency_max_ms": 8000,
            "missing_data_alert_hours": 48,
        }

    def _load_health_state(self) -> dict:
        if HEALTH_STATE_PATH.exists():
            with open(HEALTH_STATE_PATH) as f:
                return json.load(f)
        return {
            "system_status": "UNKNOWN",
            "last_check": None,
            "agent_status": {},
            "api_health": {},
            "alerts_fired": [],
        }

    def _save_health_state(self):
        HEALTH_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(HEALTH_STATE_PATH, "w") as f:
            json.dump(self.health_state, f, indent=2)

    # ── Health Checks ─────────────────────────────────────────────────────────

    def check_all(self) -> dict:
        """
        Run all health checks.
        Returns dict with status for each component.
        """
        logger.info("SENTINEL running health check")
        check_time = datetime.now(timezone.utc)

        results = {
            "timestamp": check_time.isoformat(),
            "checks": {},
            "new_alerts": [],
        }

        results["checks"]["magnus_pipeline"] = self._check_magnus_pipeline()
        results["checks"]["extraction_confidence"] = self._check_extraction_confidence()
        results["checks"]["api_latency"] = self._check_api_latency()
        results["checks"]["error_rate"] = self._check_error_rate()
        results["checks"]["data_freshness"] = self._check_data_freshness()
        results["checks"]["disk_space"] = self._check_disk_space()
        results["checks"]["agent_liveness"] = self._check_agent_liveness()

        # Aggregate system status
        alert_severities = [c.get("alert_severity") for c in results["checks"].values() if c.get("alert_severity")]
        if "CRITICAL" in alert_severities:
            system_status = "CRITICAL"
        elif "ERROR" in alert_severities:
            system_status = "DEGRADED"
        elif "WARNING" in alert_severities:
            system_status = "ATTENTION"
        else:
            system_status = "HEALTHY"

        results["system_status"] = system_status
        self.health_state["system_status"] = system_status
        self.health_state["last_check"] = check_time.isoformat()
        self.health_state["checks"] = results["checks"]

        # Fire alerts
        for check_name, check_result in results["checks"].items():
            if check_result.get("alert_severity"):
                self._maybe_alert(check_name, check_result)

        self._save_health_state()
        logger.info(f"SENTINEL health check complete: {system_status}")
        return results

    def _check_magnus_pipeline(self) -> dict:
        """Check if MAGNUS pipeline is running or stalled."""
        pipeline_state_path = PROJECT_ROOT / "memory" / "pipeline_state.json"
        if not pipeline_state_path.exists():
            return {
                "status": "WARNING",
                "alert_severity": "WARNING",
                "message": "No pipeline state file found",
                "likely_cause": "Pipeline may never have run",
            }

        with open(pipeline_state_path) as f:
            state = json.load(f)

        run_status = state.get("status", "unknown")
        stats = state.get("stats", {})

        if run_status == "running":
            start_time_str = stats.get("start_time")
            if start_time_str:
                start = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                elapsed_minutes = (datetime.now(timezone.utc) - start).total_seconds() / 60
                max_duration = self.thresholds.get("pipeline_max_duration_minutes", 240)
                if elapsed_minutes > max_duration:
                    return {
                        "status": "CRITICAL",
                        "alert_severity": "CRITICAL",
                        "message": f"Pipeline running for {elapsed_minutes:.0f} minutes (max {max_duration})",
                        "likely_cause": "Pipeline stalled or query overloaded",
                        "recovery_ref": "FAIL-04",
                    }
            return {
                "status": "OK",
                "message": f"Pipeline currently running (started {stats.get('start_time', 'unknown')})",
            }

        # Pipeline not running — check when it last completed
        last_run = stats.get("end_time")
        if not last_run:
            return {
                "status": "WARNING",
                "alert_severity": "WARNING",
                "message": "No completed pipeline run found",
                "likely_cause": "Pipeline may never have completed a run",
            }

        return {"status": "OK", "message": f"Last pipeline run: {last_run}"}

    def _check_extraction_confidence(self) -> dict:
        """Check if SIEVE extraction confidence is above minimum threshold."""
        extractions_dir = PROJECT_ROOT / "memory" / "extractions"
        if not extractions_dir.exists():
            return {"status": "UNKNOWN", "message": "No extractions found"}

        files = sorted(extractions_dir.glob("extractions_*.json"), reverse=True)
        if not files:
            return {"status": "UNKNOWN", "message": "No extraction files found"}

        with open(files[0]) as f:
            extractions = json.load(f)

        if not extractions:
            return {"status": "UNKNOWN", "message": "Empty extraction file"}

        avg_conf = sum(e.get("extraction_confidence", 0) for e in extractions) / len(extractions)
        min_conf = self.thresholds.get("extraction_confidence_min", 0.70)

        if avg_conf < min_conf:
            return {
                "status": "ERROR",
                "alert_severity": "ERROR",
                "message": f"Average extraction confidence {avg_conf:.2f} below threshold {min_conf}",
                "likely_cause": "Low-quality responses or brand name ambiguity",
                "recovery_ref": "TROUBLESHOOTING.md: extraction confidence below 0.70",
            }

        return {"status": "OK", "message": f"Average extraction confidence: {avg_conf:.2f}"}

    def _check_api_latency(self) -> dict:
        """Check if engine API latencies are within acceptable range."""
        # Would read from recent log entries or API call metrics
        # For now, use a placeholder that reads from health state
        api_health = self.health_state.get("api_health", {})
        max_latency = self.thresholds.get("api_latency_max_ms", 8000)

        slow_engines = []
        for engine, health in api_health.items():
            avg_lat = health.get("avg_latency_ms", 0)
            if avg_lat > max_latency:
                slow_engines.append(f"{engine} ({avg_lat}ms)")

        if slow_engines:
            return {
                "status": "ERROR",
                "alert_severity": "ERROR",
                "message": f"Slow engines: {', '.join(slow_engines)}",
                "likely_cause": "Proxy latency or API rate limiting",
            }

        return {"status": "OK", "message": "API latencies within normal range"}

    def _check_error_rate(self) -> dict:
        """Check pipeline error rate against maximum threshold."""
        pipeline_state_path = PROJECT_ROOT / "memory" / "pipeline_state.json"
        if not pipeline_state_path.exists():
            return {"status": "UNKNOWN"}

        with open(pipeline_state_path) as f:
            state = json.load(f)
        stats = state.get("stats", {})

        errors = stats.get("errors", 0)
        total = stats.get("prompts_queried", 0)
        if total == 0:
            return {"status": "OK", "message": "No queries yet"}

        error_rate = (errors / total) * 100
        max_rate = self.thresholds.get("error_rate_max_percent", 20)

        if error_rate > max_rate:
            return {
                "status": "ERROR",
                "alert_severity": "ERROR",
                "message": f"Error rate {error_rate:.1f}% exceeds max {max_rate}%",
                "likely_cause": "API failures or rate limiting",
            }

        return {"status": "OK", "message": f"Error rate {error_rate:.1f}% within normal range"}

    def _check_data_freshness(self) -> dict:
        """Check if we have fresh data (no 48+ hour gaps)."""
        pipeline_state_path = PROJECT_ROOT / "memory" / "pipeline_state.json"
        if not pipeline_state_path.exists():
            return {
                "status": "WARNING",
                "alert_severity": "WARNING",
                "message": "No pipeline state — data freshness unknown",
            }

        with open(pipeline_state_path) as f:
            state = json.load(f)

        last_check = state.get("stats", {}).get("end_time")
        if not last_check:
            return {
                "status": "WARNING",
                "alert_severity": "WARNING",
                "message": "No completed run found — data may be stale",
            }

        last_time = datetime.fromisoformat(last_check.replace("Z", "+00:00"))
        hours_since = (datetime.now(timezone.utc) - last_time).total_seconds() / 3600
        max_hours = self.thresholds.get("missing_data_alert_hours", 48)

        if hours_since > max_hours:
            return {
                "status": "CRITICAL",
                "alert_severity": "CRITICAL",
                "message": f"No data for {hours_since:.1f} hours (max {max_hours})",
                "likely_cause": "Pipeline stopped running or all engines returning no responses",
                "recovery_ref": "FAIL-03",
            }

        return {"status": "OK", "message": f"Data fresh: last run {hours_since:.1f}h ago"}

    def _check_disk_space(self) -> dict:
        """Check available disk space."""
        import shutil
        try:
            usage = shutil.disk_usage("/")
            free_gb = usage.free / (1024**3)
            if free_gb < 1:
                return {
                    "status": "CRITICAL",
                    "alert_severity": "CRITICAL",
                    "message": f"Disk space critically low: {free_gb:.1f}GB free",
                    "likely_cause": "Response log growing unbounded",
                    "recovery_ref": "TROUBLESHOOTING.md: DISK SPACE CRITICAL",
                }
            elif free_gb < 5:
                return {
                    "status": "WARNING",
                    "alert_severity": "WARNING",
                    "message": f"Disk space low: {free_gb:.1f}GB free",
                }
            return {"status": "OK", "message": f"Disk space: {free_gb:.1f}GB free"}
        except Exception as e:
            return {"status": "UNKNOWN", "message": f"Could not check disk space: {e}"}

    def _check_agent_liveness(self) -> dict:
        """Check if all agents have sent heartbeats recently."""
        if not AGENT_HEARTBEAT_PATH.exists():
            return {
                "status": "WARNING",
                "alert_severity": "WARNING",
                "message": "No agent heartbeat file found",
            }

        with open(AGENT_HEARTBEAT_PATH) as f:
            heartbeats = json.load(f)

        stale_agents = []
        now = datetime.now(timezone.utc).timestamp()
        max_age_seconds = self.check_interval * 3  # 3x check interval

        for agent, last_beat in heartbeats.items():
            if now - last_beat > max_age_seconds:
                stale_agents.append(agent)

        if stale_agents:
            return {
                "status": "ERROR",
                "alert_severity": "ERROR",
                "message": f"Stale agents: {', '.join(stale_agents)}",
                "likely_cause": "Agent process crashed or hung",
            }

        return {"status": "OK", "message": f"All {len(heartbeats)} agents reporting"}

    # ── Alerting ─────────────────────────────────────────────────────────────

    def _maybe_alert(self, check_name: str, result: dict):
        """Fire an alert if cooldown allows."""
        severity = result.get("alert_severity", "INFO")
        if not severity:
            return

        now = time.time()
        if now - self.last_alert_times[severity] < ALERT_COOLDOWN.get(severity, 3600):
            logger.debug(f"Alert suppressed (cooldown): {check_name} [{severity}]")
            return

        self.last_alert_times[severity] = now

        alert = {
            "alert_id": f"alert_{int(now)}_{check_name}",
            "severity": severity,
            "check_name": check_name,
            "message": result.get("message", ""),
            "likely_cause": result.get("likely_cause", ""),
            "recovery_ref": result.get("recovery_ref", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Fire to all channels for this severity
        self.alerter.send(
            level=severity,
            subject=f"ORACLE SENTINEL [{severity}]: {check_name}",
            body=f"{result.get('message', 'No details')}\n\nCause: {result.get('likely_cause', 'Unknown')}",
        )

        # Log to DB
        self._log_alert(alert)

        # Track in health state
        self.health_state.setdefault("alerts_fired", []).append(alert)

        logger.warning(f"SENTINEL ALERT [{severity}]: {check_name} — {result.get('message')}")

    def _log_alert(self, alert: dict):
        """Write alert to PostgreSQL via db_writer."""
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            return
        try:
            self.db.write_alert(alert)
        except Exception as e:
            logger.error(f"Failed to write alert to DB: {e}")

    # ── Daemon Loop ──────────────────────────────────────────────────────────

    def run_daemon(self):
        """Run SENTINEL as a daemon process."""
        self.running = True
        logger.info(f"SENTINEL daemon started (brand={self.brand}, interval={self.check_interval}s)")
        logger.info("SENTINEL is independent of MAGNUS — alerts cannot be suppressed by pipeline")

        while self.running:
            try:
                self.check_all()
            except Exception as e:
                logger.error(f"SENTINEL health check error: {e}")

            time.sleep(self.check_interval)

    def stop_daemon(self):
        """Stop the SENTINEL daemon."""
        self.running = False
        logger.info("SENTINEL daemon stopped")

    def run_once(self):
        """Run a single health check and exit."""
        return self.check_all()


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORACLE SENTINEL — System Health Monitor")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon process")
    parser.add_argument("--check-now", action="store_true", help="Run single health check and exit")
    parser.add_argument("--test-alert", action="store_true", help="Send a test alert to all channels")
    parser.add_argument("--brand", required=True, help="Brand to monitor")
    parser.add_argument("--interval", type=int, default=CHECK_INTERVAL_SECONDS,
                        help="Check interval in seconds (default 300)")
    args = parser.parse_args()

    sentinel = Sentinel(brand=args.brand, check_interval=args.interval)

    if args.daemon:
        try:
            sentinel.run_daemon()
        except KeyboardInterrupt:
            sentinel.stop_daemon()
    elif args.check_now:
        result = sentinel.run_once()
        print(json.dumps(result, indent=2))
    elif args.test_alert:
        alerter = Alerter()
        alerter.send(
            level="INFO",
            subject="ORACLE SENTINEL — Test Alert",
            body="This is a test alert from SENTINEL. Reply OK if you receive this.",
        )
        print("Test alert sent")
    else:
        parser.print_help()