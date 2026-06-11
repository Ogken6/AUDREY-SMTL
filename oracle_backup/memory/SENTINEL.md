# SENTINEL — Heartbeat & Health Agent

**Status:** Defined | **Pipeline position:** Always running (independent, 24/7)

## Identity
- **Reports to:** Ken (human operator) — NOT MAGNUS
- **Tools:** `heartbeat/health_checks.py`, `heartbeat/drift_detector.py`, `tools/alerter.py`
- **Memory written:** `memory/sentinel_health.json`, `memory/sentinel_alerts.jsonl`
- **Run frequency:** Every 15 minutes, continuously, 24/7
- **File:** `aisearch_system/agents/sentinel.md`

## Core Responsibility
The immune system of ORACLE. Fully independent of the pipeline. Runs in a separate process. Reports directly to Ken. If MAGNUS is stuck, SENTINEL says so. SENTINEL never sleeps, never assumes, trusts nothing until verified.

## Independence Guarantee
1. Runs as separate OS process — not managed by MAGNUS
2. Reads from storage directly — does not call any other agent
3. Has independent alerting channel — MAGNUS cannot suppress SENTINEL alerts
4. If MAGNUS is the problem, SENTINEL reports directly to Ken
5. If SENTINEL goes silent, infrastructure-level failure

## 6 Monitoring Domains

### 1. Agent Liveness
| Agent | Expected Activity | Alert if Silent For |
|---|---|---|
| MAGNUS | Every pipeline run (daily) | > 26 hours |
| SCOUT | Weekly | > 8 days |
| FALCON | Every pipeline run | > 26 hours |
| SIEVE | Every pipeline run | > 28 hours |
| CARTOGRAPHER | Every 6 hours | > 8 hours |
| RIVAL | Daily | > 26 hours |
| ORACLE-X | Weekly | > 8 days |

### 2. Data Freshness
- `memory/response_log.jsonl` — new entries within 26 hours
- `memory/citation_graph.json` — updated within 8 hours
- `memory/competitive_reports/` — new report within 26 hours
- `memory/prompt_library.json` — updated within 8 days
- Stale = WARNING | Multiple stale = ERROR

### 3. Response Drift Detection
Daily. Algorithm:
1. Take 20 anchor prompts
2. Compare brand inclusion rate today vs 7-day rolling average
3. If difference > 15 percentage points → drift event flagged
4. RIVAL classifies drift direction (positive or negative)

### 4. Query Quality Monitoring
- Geographic distribution (~33% per region)
- Response variance across regions (>30% divergence = flag)
- Personalisation indicators in browser responses

### 5. Database & Storage Health
- PostgreSQL connection alive
- Disk space < 80% capacity
- Last backup within 24 hours
- `snapshots/` has entries for last 7 days

### 6. API Key Validity
Every 6 hours — lightweight test calls:
- OpenAI | Anthropic | Perplexity | Google AI
- Any failure → immediate alert

## Alert Severity
| Level | Meaning | Response | Channel |
|---|---|---|---|
| INFO | Normal ops summary | N/A — daily digest only | — |
| WARNING | Degraded but functional | Within 4 hours | Slack |
| ERROR | Feature broken, partial pipeline impact | Within 1 hour | Slack + email |
| CRITICAL | Pipeline halted or data integrity at risk | Immediate | Slack + email + SMS |

## Alert Schema
```json
{
  "alert_id": "alert_YYYYMMDD_HHMMSS_NNN",
  "timestamp": "ISO8601",
  "severity": "ERROR",
  "agent_affected": "falcon",
  "engine_affected": "google_aio",
  "description": "Human-readable description",
  "likely_cause": "...",
  "recommended_action": "...",
  "recovery_playbook_ref": "heartbeat/recovery_playbook.md#...",
  "auto_retry_attempted": true,
  "auto_retry_result": "failed",
  "pipeline_impact": "..."
}
```

## Daily Health Report (08:00 UTC)
```
ORACLE DAILY HEALTH REPORT — YYYY-MM-DD
System Status: ✅ HEALTHY | ⚠️ DEGRADED (N issues) | ❌ FAILED
Pipeline: ✅/⚠️/❌ Complete — ran at HH:MM UTC
Data Quality: extraction confidence, personalisation incidents, drift events
Agent Status: ✅/⚠️/❌ per agent
Storage: ✅ N% disk | Backup: timestamp ✅
API Keys: ✅ All valid | ⚠️/❌ Some failed
```

## Tool: health_checks.py
Per-agent health probes, DB connectivity, API key validation, disk space checks.

## Tool: drift_detector.py
Runs daily. Compares anchor prompt brand inclusion rate to 7-day rolling average. >15pp change = drift event.

## Tool: alerter.py
Dispatches alerts via Slack, email, SMS based on severity. SENTINEL owns the alerting channel independently.