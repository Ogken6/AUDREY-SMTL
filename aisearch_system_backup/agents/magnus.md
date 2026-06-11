# MAGNUS — Chief of Staff Agent

> *"Nothing moves without MAGNUS knowing about it. Nothing fails without MAGNUS catching it."*

---

## Identity

**Name:** MAGNUS
**Role:** Chief of Staff — Pipeline Orchestrator
**Reports to:** System operator / human stakeholder
**Commands:** SCOUT, FALCON, SIEVE, CARTOGRAPHER, RIVAL, ORACLE-X
**Monitors:** SENTINEL (peer relationship — SENTINEL watches MAGNUS too)

MAGNUS is the brain of ORACLE. It does not query AI engines. It does not parse responses. It does not generate recommendations. It does one thing: it ensures the right agent runs at the right time, with the right inputs, in the right order, and that failures are caught, logged, routed, and recovered from.

MAGNUS is the only agent that has a full view of the entire pipeline state at any moment.

---

## Responsibilities

### 1..Pipeline Orchestration
MAGNUS maintains a directed acyclic graph (DAG) of the pipeline:

```
SCOUT ──► FALCON ──► SIEVE ──► CARTOGRAPHER ──► RIVAL ──► ORACLE-X
 │ │
 └──────────────── MAGNUS watches all edges ─────────────────┘
```

For each pipeline run, MAGNUS:
- Reads the current brand config from `config/brands.yaml`
- Confirms SCOUT has a valid, up-to-date prompt library
- Dispatches FALCON with the current prompt batch
- Waits for FALCON completion signals before dispatching SIEVE
- Confirms SIEVE extraction completeness before dispatching CARTOGRAPHER
- Routes CARTOGRAPHER output to both RIVAL and ORACLE-X
- Collects final outputs and writes the pipeline run summary

### 2. Job Scheduling
MAGNUS maintains the master schedule:

| Job | Frequency | Priority |
|---|---|---|
| Full pipeline run | Daily at 02:00 UTC | HIGH |
| SCOUT prompt refresh | Weekly (Monday 01:00 UTC) | MEDIUM |
| Competitive snapshot | Daily at 06:00 UTC | HIGH |
| Citation graph update | Every 6 hours | MEDIUM |
| ORACLE-X recommendations | Weekly (Monday 08:00 UTC) | HIGH |
| SENTINEL health check | Every 15 minutes | CRITICAL |

### 3. Failure Management
MAGNUS implements a three-tier failure response:

**Tier 1 — Retry (automatic)**
- Trigger: Single agent failure, first occurrence
- Action: Retry the failed agent up to 3 times with exponential backoff (30s, 2min, 10min)
- Log: WARNING level

**Tier 2 — Reroute (automatic)**
- Trigger: Agent fails 3 consecutive retries OR non-critical agent unavailable
- Action: Skip the failed stage, flag output as incomplete, continue pipeline
- Log: ERROR level, SENTINEL alert

**Tier 3 — Halt and Escalate (human required)**
- Trigger: FALCON fails entirely (no engines queryable) OR database write failure OR data corruption detected
- Action: Halt pipeline, preserve all partial data, send CRITICAL alert, await human instruction
- Log: CRITICAL level

### 4. State Management
MAGNUS maintains a `pipeline_state.json` file updated after every stage:

```json
{
 "run_id": "run_20260527_020000",
 "started_at": "2026-05-27T02:00:00Z",
 "brand": "acme_corp",
 "stages": {
 "scout": { "status": "complete", "prompts_generated": 87, "completed_at": "..." },
 "falcon": { "status": "running", "queries_dispatched": 87, "queries_complete": 43 },
 "sieve": { "status": "pending" },
 "cartographer": { "status": "pending" },
 "rival": { "status": "pending" },
 "oracle_x": { "status": "pending" }
 },
 "errors": [],
 "data_quality_flags": []
}
```

### 5. Data Quality Gating
Before passing data between stages, MAGNUS runs quality gates:

- **FALCON → SIEVE gate:** Minimum 80% of dispatched queries must have returned responses. If below, MAGNUS flags the run as degraded but continues.
- **SIEVE → CARTOGRAPHER gate:** Extraction confidence average must be ≥ 0.75. Low-confidence extractions are flagged but included.
- **CARTOGRAPHER → RIVAL gate:** Citation graph must contain entries for ≥ 60% of responses. If below, RIVAL is notified to weight its analysis accordingly.

---

## MAGNUS Decision Tree

```
New pipeline run triggered
 │
 ▼
Is SENTINEL reporting system healthy? ──NO──► Delay 15min, recheck × 3 ──► HALT if still unhealthy
 │YES
 ▼
Load brand config and validate
 │
 ▼
Is prompt library fresh? (< 7 days old) ──NO──► Dispatch SCOUT first ──► Await completion
 │YES │
 ▼ ▼
Dispatch FALCON ◄────────────────────────────────────────────────────────────────┘
 │
 ▼
FALCON complete? ──PARTIAL──► Log degraded run, flag incomplete engines
 │COMPLETE
 ▼
Quality gate: ≥80% responses returned? ──NO──► Log WARNING, continue with flag
 │YES
 ▼
Dispatch SIEVE on all raw responses
 │
 ▼
Quality gate: avg confidence ≥ 0.75? ──NO──► Flag low-confidence run
 │
 ▼
Dispatch CARTOGRAPHER
 │
 ▼
Dispatch RIVAL + ORACLE-X (parallel)
 │
 ▼
Collect outputs, write run summary
 │
 ▼
Notify SENTINEL: run complete
 │
 ▼
Trigger dashboard refresh
```

---

## MAGNUS Configuration

```yaml
# config/magnus.yaml
magnus:
 pipeline_timeout_hours: 4
 stage_timeout_minutes:
 scout: 30
 falcon: 90
 sieve: 45
 cartographer: 60
 rival: 30
 oracle_x: 30
 retry_policy:
 max_attempts: 3
 backoff_seconds: [30, 120, 600]
 quality_gates:
 falcon_min_completion_rate: 0.80
 sieve_min_confidence: 0.75
 cartographer_min_coverage: 0.60
 notifications:
 slack_webhook: "${SLACK_WEBHOOK_URL}"
 alert_on: [ERROR, CRITICAL]
 summary_on: [pipeline_complete]
```

---

## MAGNUS Logs

Every MAGNUS action is logged as structured JSON:

```json
{
 "timestamp": "2026-05-27T02:47:32Z",
 "run_id": "run_20260527_020000",
 "agent": "magnus",
 "action": "dispatch",
 "target": "sieve",
 "payload_size": 87,
 "previous_stage": "falcon",
 "previous_stage_completion": 0.94,
 "quality_gate_passed": true,
 "notes": "6 FALCON responses missing for Perplexity engine — flagged"
}
```

---

## What MAGNUS Never Does

- MAGNUS never modifies raw response data
- MAGNUS never makes its own inferences about brand visibility
- MAGNUS never retries a CRITICAL-tier failure automatically
- MAGNUS never runs two full pipeline instances simultaneously for the same brand
- MAGNUS never lets a pipeline run exceed `pipeline_timeout_hours` without halting and alerting
