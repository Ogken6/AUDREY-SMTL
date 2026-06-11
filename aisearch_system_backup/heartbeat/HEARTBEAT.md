# HEARTBEAT.md — ORACLE Heartbeat System Design

> *"A system that doesn't know it's broken is a system that's already failing its users."*

---

## Philosophy

ORACLE's heartbeat system is not an afterthought. It is infrastructure. SENTINEL, the heartbeat agent, is designed on the assumption that every other component will eventually fail — and ORACLE's job is to know about it before the humans who depend on it do.

The heartbeat system answers three questions continuously:
1. **Is everything running?** (Liveness)
2. **Is the data still reliable?** (Freshness + Drift)
3. **If something broke, what exactly is broken and how do we fix it?** (Diagnosis + Recovery)

---

## Heartbeat Architecture

```
SENTINEL (runs every 15 minutes, independent process)
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
**Check:** Is each agent's last activity timestamp within its expected window?
**Run frequency:** Every 15 minutes
**Method:** Read `pipeline_state.json` and each agent's log file for last activity timestamp
**Alert threshold:** See `agents/sentinel.md` — Agent Liveness table

### HC-02: Data Freshness
**Check:** Have key memory files been updated on schedule?
**Run frequency:** Every 15 minutes
**Method:** Check file modification timestamps against expected update intervals
**Alert threshold:** 120% of expected interval triggers WARNING; 200% triggers ERROR

### HC-03: API Key Validity
**Check:** Are all external API keys valid and not expired/rate-limited?
**Run frequency:** Every 6 hours
**Method:** Minimal test call to each API (1 token, "ping" prompt)
**Alert threshold:** Any key failure = immediate ERROR alert

### HC-04: Proxy Pool Health
**Check:** Is the proxy pool large enough to support a full pipeline run?
**Run frequency:** Every 30 minutes
**Method:** Query proxy provider API for available IP count per region
**Alert threshold:** Available IPs < 30 per region = WARNING; < 10 = CRITICAL (FALCON cannot run)

### HC-05: Database Health
**Check:** Is PostgreSQL reachable, responding within latency threshold, and backed up?
**Run frequency:** Every 15 minutes
**Method:** SELECT 1 query; check backup timestamp
**Alert threshold:** Connection failure = CRITICAL; latency > 2s = WARNING; backup > 25h old = ERROR

### HC-06: Disk Space
**Check:** Is storage capacity sufficient for ongoing operation?
**Run frequency:** Every hour
**Method:** Check disk usage on response log storage
**Alert threshold:** > 70% = WARNING; > 85% = ERROR (trigger archive job); > 95% = CRITICAL

### HC-07: Response Drift
**Check:** Have AI engine responses about the brand shifted unexpectedly?
**Run frequency:** Daily, after each full pipeline run
**Method:** See `drift_detector.py` below
**Alert threshold:** ±15 percentage points vs 7-day rolling average on any anchor prompt = drift event

### HC-08: Pipeline Run Completion
**Check:** Did the last scheduled pipeline run complete within the expected window?
**Run frequency:** Check at 06:00 UTC daily (4 hours after scheduled run start)
**Method:** Read `pipeline_state.json` — all stages should show `complete`
**Alert threshold:** Any stage in `pending` or `running` at 06:00 UTC = ERROR

---

## `drift_detector.py` — How Drift Detection Works

Drift detection is SENTINEL's most sophisticated capability. It catches invisible problems — AI engines gradually changing how they describe the brand, without any visible system failure.

```python
def detect_drift(brand, anchor_prompts, lookback_days=7):
    """
    Compare today's brand inclusion rate on anchor prompts
    against the 7-day rolling average.
    """
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

            # Drift = absolute change from rolling average
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

**What drift can mean:**
- **Positive drift (brand appearing more):** New positive source added/cited; competitor lost visibility; model update favouring brand's content
- **Negative drift (brand appearing less):** New source cited that omits brand; competitor gained strong new citation; model update; brand's cited sources changed

Drift events are passed to RIVAL for full analysis on the next run.

---

## Recovery Playbook

### FAIL-01: Google AIO Selector Failure
**Symptom:** FALCON reports 0 Google AIO responses; `selector_not_found` errors
**Cause:** Google updated AI Overview page HTML structure
**Recovery steps:**
1. Open a real Chrome browser and run one of the anchor prompts manually on Google
2. Right-click the AI Overview box → Inspect
3. Find the container element class name
4. Update `tools/browser_agent.py` → `SELECTORS["google_aio"]`
5. Run one test query: `python tools/browser_agent.py --test --engine=google_aio`
6. If successful, clear SENTINEL alert and resume FALCON

**Estimated fix time:** 15–30 minutes
**Impact if delayed:** Google AIO data gap in current run; no data corruption

---

### FAIL-02: OpenAI API Key Expired or Rate Limited
**Symptom:** HC-03 fails; FALCON ChatGPT queries all return 401 or 429
**Recovery steps:**
1. Check OpenAI dashboard for key status and rate limit consumption
2. If rate limited: FALCON will auto-pause ChatGPT queries for 30 minutes. If still limited after 30 min, manually increase rate limit tier on OpenAI dashboard.
3. If key expired/revoked: Generate new key, update `OPENAI_API_KEY` environment variable, restart FALCON

**Estimated fix time:** 5–60 minutes (depends on cause)
**Impact if delayed:** ChatGPT data missing from current run

---

### FAIL-03: Proxy Pool Exhausted
**Symptom:** HC-04 critical; proxy pool available < 10 IPs per region
**Recovery steps:**
1. Check proxy provider dashboard for blocked IPs (mass block events happen occasionally)
2. If mass block: Contact proxy provider, request IP pool refresh
3. If normal depletion: Trigger manual pool expansion in provider dashboard (add 50 IPs per region)
4. Interim: Reduce FALCON concurrent query rate by 50% to reduce IP turnover

**Estimated fix time:** 30 minutes – 2 hours
**Impact if delayed:** FALCON runs at reduced capacity or pauses entirely

---

### FAIL-04: Database Write Failure
**Symptom:** `db_writer.py` returns transaction errors; pipeline stage outputs not persisted
**Recovery steps:**
1. Check PostgreSQL connection: `psql $DATABASE_URL -c "SELECT 1"`
2. Check disk space on database server (common cause)
3. Check connection pool — restart connection pool if exhausted
4. **Do not rerun failed pipeline stages yet** — wait for DB to stabilise
5. Once DB is healthy, MAGNUS can safely rerun the failed stage (idempotent)

**Estimated fix time:** 15–60 minutes
**Impact if delayed:** Data loss for the affected pipeline run stage

---

### FAIL-05: `response_log.jsonl` Corruption
**Symptom:** SIEVE fails to parse jsonl file; SENTINEL detects malformed records
**Recovery steps:**
1. **Stop all writes immediately** — halt FALCON if running
2. Identify last valid line: `python -c "import json; [json.loads(l) for l in open('memory/response_log.jsonl')]"` — last successful parse = last valid record
3. Truncate file to last valid record
4. Restore any lost records from `memory/snapshots/responses_YYYYMMDD.jsonl`
5. Resume pipeline from SIEVE stage (FALCON data is in snapshots)

**Estimated fix time:** 30–90 minutes
**Impact:** Potential data loss for records written after last valid entry; no structural damage to historical data

---

### FAIL-06: Full Pipeline Silence (MAGNUS Unresponsive)
**Symptom:** No pipeline activity for > 26 hours; `pipeline_state.json` not updated
**Recovery steps:**
1. Check MAGNUS process: `ps aux | grep magnus`
2. If process dead: Check logs at `logs/magnus.log` for crash reason
3. If OOM killed: Increase memory allocation; restart
4. If hung: Kill process; run `python agents/magnus.py --check-state` to assess partial run state
5. If partial run in progress: Run `python agents/magnus.py --resume --run-id=<last_run_id>`
6. If no partial run: Start fresh run with `python agents/magnus.py --run-now`

**Estimated fix time:** 30 minutes – 2 hours
**Impact:** Data gap for the missed pipeline run
