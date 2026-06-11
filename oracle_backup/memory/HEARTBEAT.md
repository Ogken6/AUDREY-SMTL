# HEARTBEAT.md — ORACLE Heartbeat System Design

> *"A system that doesn't know it's broken is a system that's already failing its users."*

**Owner:** SENTINEL | **File:** `aisearch_system/heartbeat/HEARTBEAT.md`

---

## Philosophy

ORACLE's heartbeat system is not an afterthought. It is infrastructure.

SENTINEL is designed on the assumption that every other component will eventually fail — and ORACLE's job is to know about it before the humans who depend on it do.

Three questions SENTINEL answers continuously:
1. **Is everything running?** — Liveness
2. **Is the data still reliable?** — Freshness + Drift
3. **If something broke, what exactly is broken and how do we fix it?** — Diagnosis + Recovery

---

## Heartbeat Architecture

```
SENTINEL (every 15 minutes, independent process)
 │
 ├── health_checks.py ← Agent liveness, API keys, storage, DB
 ├── drift_detector.py ← Response drift analysis (daily)
 └── alerter.py ← Routes alerts by severity
 │
 ├── Slack (#oracle-alerts)
 ├── Email (ops team)
 └── SMS (CRITICAL only, on-call)
```

---

## Health Check Definitions

### HC-01: Agent Liveness
**Check:** Each agent's last activity timestamp within expected window?
**Frequency:** Every 15 minutes
**Method:** Read `pipeline_state.json` + each agent's log file for last activity timestamp
**Alert:** See `memory/SENTINEL.md` — Agent Liveness table

### HC-02: Data Freshness
**Check:** Key memory files updated on schedule?
**Frequency:** Every 15 minutes
**Method:** Check file modification timestamps against expected update intervals
**Alert:** 120% of expected interval → WARNING; 200% → ERROR

### HC-03: API Key Validity
**Check:** All external API keys valid and not expired/rate-limited?
**Frequency:** Every 6 hours
**Method:** Minimal test call to each API (1 token, "ping" prompt)
**Alert:** Any key failure = immediate ERROR

### HC-04: Proxy Pool Health
**Check:** Proxy pool large enough to support full pipeline run?
**Frequency:** Every 30 minutes
**Method:** Query proxy provider API for available IP count per region
**Alert:** Available IPs < 30/region → WARNING; < 10 → CRITICAL (FALCON cannot run)

### HC-05: Database Health
**Check:** PostgreSQL reachable, responding within latency threshold, and backed up?
**Frequency:** Every 15 minutes
**Method:** `SELECT 1` query; check backup timestamp
**Alert:** Connection failure → CRITICAL; latency > 2s → WARNING; backup > 25h old → ERROR

### HC-06: Disk Space
**Check:** Storage capacity sufficient?
**Frequency:** Every hour
**Method:** Check disk usage on response log storage
**Alert:** > 70% → WARNING; > 85% → ERROR (trigger archive job); > 95% → CRITICAL

### HC-07: Response Drift
**Check:** Have AI engine responses about the brand shifted unexpectedly?
**Frequency:** Daily after each full pipeline run
**Method:** See `drift_detector.py` section below
**Alert:** ±15 percentage points vs 7-day rolling average on any anchor prompt → drift event

### HC-08: Pipeline Run Completion
**Check:** Did last scheduled pipeline run complete within expected window?
**Frequency:** Check at 06:00 UTC daily (4h after scheduled run start)
**Method:** Read `pipeline_state.json` — all stages should show `complete`
**Alert:** Any stage in `pending` or `running` at 06:00 UTC → ERROR

---

## `drift_detector.py` — How Drift Detection Works

Drift detection catches invisible problems — AI engines gradually changing how they describe the brand, without any visible system failure.

```python
def detect_drift(brand, anchor_prompts, lookback_days=7):
    today_rates = {}
    rolling_rates = {}
    drift_events = []

    for prompt in anchor_prompts:
        for engine in ENGINES:
            # Today's rate
            today_responses = get_responses(prompt.id, engine, days=1)
            today_rate = calculate_inclusion_rate(today_responses, brand)

            # 7-day rolling average
            rolling_responses = get_responses(prompt.id, engine, days=lookback_days)
            rolling_rate = calculate_inclusion_rate(rolling_responses, brand)

            drift = abs(today_rate - rolling_rate)

            if drift > DRIFT_THRESHOLD:  # 0.15 = 15 percentage points
                drift_events.append({
                    "prompt_id": prompt.id,
                    "engine": engine,
                    "today_rate": today_rate,
                    "rolling_avg_rate": rolling_rate,
                    "drift_magnitude": drift,
                    "drift_direction": "positive" if today_rate > rolling_rate else "negative",
                    "severity": "high" if drift > 0.25 else "medium"
                })

    return drift_events
```

**What drift means:**
- **Positive drift:** New positive source added/cited; competitor lost visibility; model update favouring brand
- **Negative drift:** New source cited that omits brand; competitor gained visibility; model/content update

Drift events passed to RIVAL for full analysis on the next run.

---

## Recovery Playbook

### FAIL-01: Google AIO Selector Failure
**Symptom:** FALCON 0 Google AIO responses; `selector_not_found` errors
**Cause:** Google updated AI Overview page HTML structure
**Recovery:**
1. Open real Chrome, run anchor prompt manually on Google
2. Right-click AI Overview box → Inspect
3. Find container element class name
4. Update `tools/browser_agent.py` → `SELECTORS["google_aio"]`
5. Test: `python tools/browser_agent.py --test --engine=google_aio`
6. If successful: clear SENTINEL alert, resume FALCON

**Fix time:** 15–30 min | **Impact:** Google AIO data gap, no data corruption

---

### FAIL-02: OpenAI API Key Expired or Rate Limited
**Symptom:** HC-03 fails; FALCON ChatGPT queries return 401 or 429
**Recovery:**
1. Check OpenAI dashboard for key status and rate limit consumption
2. If rate limited: FALCON auto-pauses ChatGPT queries 30 min. If still limited, manually increase rate limit tier on OpenAI dashboard.
3. If key expired/revoked: Generate new key, update `OPENAI_API_KEY`, restart FALCON

**Fix time:** 5–60 min | **Impact:** ChatGPT data missing from current run

---

### FAIL-03: Proxy Pool Exhausted
**Symptom:** HC-04 critical; proxy pool available < 10 IPs per region
**Recovery:**
1. Check proxy provider dashboard for blocked IPs
2. If mass block: Contact provider, request IP pool refresh
3. If normal depletion: Trigger pool expansion (add 50 IPs/region)
4. Interim: Reduce FALCON concurrent query rate by 50%

**Fix time:** 30 min – 2h | **Impact:** FALCON runs at reduced capacity or pauses

---

### FAIL-04: Database Write Failure
**Symptom:** `db_writer.py` transaction errors; pipeline stage outputs not persisted
**Recovery:**
1. Check PostgreSQL: `psql $DATABASE_URL -c "SELECT 1"`
2. Check disk space on DB server
3. Check connection pool — restart if exhausted
4. **Do not rerun failed stages yet** — wait for DB to stabilise
5. Once healthy: MAGNUS can safely rerun failed stage (idempotent)

**Fix time:** 15–60 min | **Impact:** Data loss for affected pipeline stage

---

### FAIL-05: `response_log.jsonl` Corruption
**Symptom:** SIEVE fails to parse jsonl; SENTINEL detects malformed records
**Recovery:**
1. **Stop all writes immediately** — halt FALCON if running
2. Identify last valid line: parse file, last successful parse = last valid record
3. Truncate file to last valid record
4. Restore lost records from `memory/snapshots/responses_YYYYMMDD.jsonl`
5. Resume pipeline from SIEVE stage (FALCON data is in snapshots)

**Fix time:** 30–90 min | **Impact:** Potential data loss for records after last valid entry; no damage to historical data

---

### FAIL-06: Full Pipeline Silence (MAGNUS Unresponsive)
**Symptom:** No pipeline activity for > 26h; `pipeline_state.json` not updated
**Recovery:**
1. Check MAGNUS process: `ps aux | grep magnus`
2. If dead: Check `logs/magnus.log` for crash reason
3. If OOM killed: Increase memory; restart
4. If hung: Kill process; run `python agents/magnus.py --check-state`
5. If partial run in progress: `python agents/magnus.py --resume --run-id=<last_run_id>`
6. If no partial run: `python agents/magnus.py --run-now`

**Fix time:** 30 min – 2h | **Impact:** Data gap for missed pipeline run