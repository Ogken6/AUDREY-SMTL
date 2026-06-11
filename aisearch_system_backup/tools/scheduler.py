#!/usr/bin/env python3
"""
scheduler.py — Job scheduling and queue management for MAGNUS
Supports cron expressions, one-time delayed runs, and recurring schedules.
"""

import os
import time
import json
import logging
import threading
from datetime import datetime
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class Scheduler:
    """
    Job scheduler for MAGNUS pipeline runs and SENTINEL health checks.
    Supports Redis backend for distributed scheduling, or in-process fallback.
    """

    def __init__(self, backend: str = "memory", redis_url: Optional[str] = None):
        self.backend = backend
        self.redis_url = redis_url or os.environ.get("REDIS_URL")
        self._queue = []
        self._running = {}
        self._lock = threading.Lock()
        self._daemon_thread = None
        self._stop = False

        if backend == "redis" and self.redis_url:
            try:
                import redis
                self._redis = redis.from_url(self.redis_url)
            except Exception:
                logger.warning("Redis connection failed — falling back to memory backend")
                self.backend = "memory"
                self._redis = None
        else:
            self._redis = None

    def schedule_once(
        self,
        job_name: str,
        agent: str,
        run_at: str,  # ISO8601 timestamp
        params: Optional[dict] = None,
    ) -> str:
        """Schedule a one-time job at a specific UTC time. Returns job_id."""
        run_at_ts = datetime.fromisoformat(run_at.replace("Z", "+00:00")).timestamp()
        job_id = f"{job_name}_{int(run_at_ts)}"
        job = {
            "job_id": job_id,
            "job_name": job_name,
            "agent": agent,
            "run_at": run_at_ts,
            "params": params or {},
            "status": "pending",
            "type": "once",
        }
        if self.backend == "redis":
            self._redis.rpush("oracle:scheduler:queue", json.dumps(job))
        else:
            with self._lock:
                self._queue.append(job)
        logger.info(f"Scheduled one-time job: {job_id} at {run_at}")
        return job_id

    def schedule_recurring(
        self,
        job_name: str,
        agent: str,
        cron: str,  # 5-part cron expression
        params: Optional[dict] = None,
    ) -> str:
        """Schedule a recurring job via cron expression. Returns job_id."""
        job_id = f"{job_name}_recurring"
        job = {
            "job_id": job_id,
            "job_name": job_name,
            "agent": agent,
            "cron": cron,
            "params": params or {},
            "status": "active",
            "type": "recurring",
        }
        if self.backend == "redis":
            self._redis.hset("oracle:scheduler:recurring", job_id, json.dumps(job))
        else:
            with self._lock:
                existing = [j for j in self._queue if j["job_id"] == job_id]
                if existing:
                    self._queue = [j for j in self._queue if j["job_id"] != job_id]
                self._queue.append(job)
        logger.info(f"Scheduled recurring job: {job_id} with cron: {cron}")
        return job_id

    def queue_status(self) -> dict:
        """Return current queue status."""
        if self.backend == "redis":
            pending = self._redis.llen("oracle:scheduler:queue")
            running = self._redis.scard("oracle:scheduler:running")
        else:
            with self._lock:
                now = time.time()
                pending = len([j for j in self._queue if j["run_at"] > now])
                running = len(self._running)
        return {
            "pending": pending,
            "running": running,
            "failed": 0,
            "backend": self.backend,
        }

    def start_daemon(self):
        """Start the scheduler daemon loop in a background thread."""
        self._stop = False
        self._daemon_thread = threading.Thread(target=self._daemon_loop, daemon=True)
        self._daemon_thread.start()
        logger.info("Scheduler daemon started")

    def stop(self):
        """Stop the scheduler daemon."""
        self._stop = True
        if self._daemon_thread:
            self._daemon_thread.join(timeout=5)
        logger.info("Scheduler daemon stopped")

    def _daemon_loop(self):
        """Main scheduler loop — checks queue every 30 seconds."""
        while not self._stop:
            self._evaluate_queue()
            time.sleep(30)

    def _evaluate_queue(self):
        """Evaluate pending jobs and dispatch any that are due."""
        now = time.time()
        if self.backend == "redis":
            jobs = self._redis.lrange("oracle:scheduler:queue", 0, -1)
            for job_json in jobs:
                import redis
                job = json.loads(job_json)
                if job["run_at"] <= now:
                    self._redis.lrem("oracle:scheduler:queue", 1, job_json)
                    self._dispatch(job)
        else:
            with self._lock:
                due = [j for j in self._queue
                       if j["type"] == "once" and j["run_at"] <= now and j["status"] == "pending"]
                for job in due:
                    self._dispatch(job)
                    job["status"] = "dispatched"

    def _dispatch(self, job: dict):
        """Dispatch a job by writing its params to the MAGNUS queue file."""
        queue_file = "/root/.openclaw/workspace/aisearch_system/memory/magnus_queue.json"
        import json
        queue_entry = {
            "job_id": job["job_id"],
            "job_name": job["job_name"],
            "agent": job["agent"],
            "params": job["params"],
            "dispatched_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(queue_file, "a") as f:
            f.write(json.dumps(queue_entry) + "\n")
        logger.info(f"Dispatched job: {job['job_id']}")
