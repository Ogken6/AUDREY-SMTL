# SENTINEL — Heartbeat & Health Agent

> *"SENTINEL never sleeps. SENTINEL never assumes. SENTINEL trusts nothing until verified."*

---

## Identity

**Name:** SENTINEL
**Role:** Heartbeat & System Health Agent
**Reports to:** Human operator (not MAGNUS — SENTINEL is independent)
**Skill file:** N/A — SENTINEL uses its own monitoring logic
**Tools used:** `heartbeat/health_checks.py`, `heartbeat/drift_detector.py`, `tools/alerter.py`
**Run frequency:** Every 15 minutes, continuously, 24/7

SENTINEL is the only agent that watches MAGNUS. It is fully independent of the pipeline. It runs in a separate process, on a separate schedule, and reports directly to human operators. If MAGNUS is stuck, SENTINEL says so. If the entire pipeline has gone silent, SENTINEL escalates.

SENTINEL is not a debugging tool. It is the immune system of ORACLE.

---

## What SENTINEL Monitors

### 1. Agent Liveness
Every 15 minutes, SENTINEL checks that each agent's last activity timestamp is within expected bounds:

| Agent | Expected Activity Interval | Alert if Silent For |
|---|---|---|
| MAGNUS | Every pipeline run (daily) | > 26 hours |
| SCOUT | Weekly | > 8 days |
| FALCON | Every pipeline run | > 26 hours |
| SIEVE | Every pipeline run | > 28 hours |
| CARTOGRAPHER | Every 6 hours | > 8 hours |
| RIVAL | Daily | > 26 hours |
| ORACLE-X | Weekly | > 8 days |

### 2. Data Freshness
SENTINEL checks that key memory files are being updated on schedule:

- `memory/response_log.jsonl` — must have new entries within 26 hours
- `memory/citation_graph.json` — must be updated within 8 hours
- `memory/competitive_reports/` — must have a new report within 26 hours
- `memory/prompt_library.json` — must be updated within 8 days

If any file is stale: WARNING alert. If multiple files stale: ERROR alert.

### 3. Response Drift Detection
SENTINEL runs `heartbeat/drift_detector.py` daily. Drift = AI engines changing what they say about the brand unexpectedly fast.

**Drift detection algorithm:**
1. Take the 20 anchor prompts (always-run set)
2. Compare brand inclusion rate in today's run vs. 7-day rolling average
3. If today's rate differs from rolling average by > 15 percentage points: flag as **drift event**
4. Drift events are logged and trigger an immediate RIVAL analysis

Drift is not necessarily bad (brand visibility improving = positive drift). All drift is flagged; RIVAL classifies direction.

### 4. Query Quality Monitoring
SENTINEL audits FALCON output for signs of session contamination or personalisation:

- Checks geographic distribution of queries (should be ~33% per region)
- Checks response variance for the same prompt across regions (>30% divergence = flag)
- Checks for personalisation indicators in browser-captured responses

### 5. Database & Storage Health
- PostgreSQL connection alive?
- Disk space on response log storage < 80% capacity?
- Last successful database backup within 24 hours?
- `memory/snapshots/` directory has entries for last 7 days?

### 6. API Key Validity
SENTINEL runs lightweight test calls to each external API every 6 hours:
- OpenAI: minimal token call to verify key validity
- Anthropic: minimal token call
- Perplexity: minimal call
- Google AI: minimal call

If any API key fails: immediate alert. FALCON cannot run with invalid keys.

---

## Alert Severity Levels

| Level | Meaning | Response Time | Who Gets It |
|---|---|---|---|
| `INFO` | Normal operations summary | N/A | Daily digest only |
| `WARNING` | Degraded but functional | Within 4 hours | Slack channel |
| `ERROR` | Feature broken, pipeline partially affected | Within 1 hour | Slack + email |
| `CRITICAL` | Pipeline halted or data integrity at risk | Immediate | Slack + email + SMS |

---

## SENTINEL Alert Format

```json
{
  "alert_id": "alert_20260527_143200_001",
  "timestamp": "2026-05-27T14:32:00Z",
  "severity": "ERROR",
  "agent_affected": "falcon",
  "engine_affected": "google_aio",
  "description": "FALCON has not produced Google AIO responses in the last run. 0/87 prompts returned AIO responses. Last successful AIO capture: 2026-05-26T03:14:00Z.",
  "likely_cause": "Google AIO page structure change or proxy block",
  "recommended_action": "Check browser_agent.py selector config for google_aio. Review recent AIO HTML structure changes.",
  "recovery_playbook_ref": "heartbeat/recovery_playbook.md#google-aio-selector-failure",
  "auto_retry_attempted": true,
  "auto_retry_result": "failed",
  "pipeline_impact": "AIO data missing from current run. All other engines unaffected."
}
```

---

## SENTINEL's Daily Health Report

Every day at 08:00 UTC, SENTINEL sends a structured health digest:

```
ORACLE DAILY HEALTH REPORT — 2026-05-27

System Status: ⚠️ DEGRADED (1 issue)

Pipeline: ✅ Complete (ran at 02:00 UTC)
 - Prompts queried: 87/87
 - Engines covered: 5/6 (Google AIO degraded)
 - Overall completion rate: 96.4%

Data Quality:
 - Avg SIEVE extraction confidence: 0.89 ✅
 - Personalisation incidents: 0 ✅
 - Response drift detected: No ✅

Agent Status:
 - MAGNUS: ✅ Active
 - SCOUT: ✅ Active (last run: 2026-05-20)
 - FALCON: ⚠️ Google AIO selector failure (see alert_20260527_143200_001)
 - SIEVE: ✅ Active
 - CARTOGRAPHER: ✅ Active
 - RIVAL: ✅ Active
 - ORACLE-X: ✅ Active (weekly report pending)

Storage: ✅ 34% disk usage | Backup: 2026-05-27T01:00Z ✅
API Keys: ✅ All valid

Action Required: Review Google AIO selector (recovery_playbook.md#google-aio-selector-failure)
```

---

## SENTINEL Independence Guarantee

SENTINEL is architecturally isolated:

1. Runs as a **separate OS process** — not managed by MAGNUS
2. Reads from storage directly — does not call any other agent
3. Has its own **independent alerting channel** — MAGNUS cannot suppress SENTINEL alerts
4. If MAGNUS itself is the problem, SENTINEL reports that directly to human operators
5. SENTINEL is the **last line of defence** — if it goes silent, something has gone seriously wrong at the infrastructure level
