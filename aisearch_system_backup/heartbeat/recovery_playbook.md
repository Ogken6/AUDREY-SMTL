# SENTINEL Recovery Playbook

Reference guide for recovering from each failure scenario SENTINEL can detect.

---

## Google AIO Selector Failure

**Alert:** `FALCON has not produced Google AIO responses. 0/N prompts returned AIO responses.`

**Likely causes:**
1. Google changed page DOM structure — selectors broke
2. AI Overview not triggered for query set (geographic/IP mismatch)
3. Proxy blocked by Google

**Recovery steps:**
1. Run: `python heartbeat/drift_detector.py --check-aio` to confirm extent
2. Inspect Google SERP manually: visit `google.com/search?q=test&AI_OVERVIEW` in browser
3. Update `browser_agent.py` `_find_query_input()` selectors for current Google DOM
4. Test: `python tools/browser_agent.py --engine google_aio --query "best recipe websites UK"`
5. If proxy block suspected: rotate proxy pool via `python tools/proxy_manager.py --reset`
6. Re-run FALCON for google_aio engine only: `python agents/falcons.py --engine google_aio --run-now`

---

## FALCON Rate Limit Sustained (429 on same engine >3 times)

**Alert:** `FALCON engine [engine] hitting persistent rate limits. Pause initiated.`

**Recovery steps:**
1. Do NOT manually re-enable the engine — SENTINEL enforces the 30-min pause
2. After 30 min: run `python heartbeat/health_checks.py --run-now` to confirm recovery
3. If persists past 2 hours: check API quota dashboard for the provider
4. If key issue confirmed: rotate API key and update environment variable

---

## SIEVE Extraction Confidence Low (<0.75 average)

**Alert:** `SIEVE extraction confidence degraded. Avg: 0.XX`

**Likely causes:**
1. AI engine responses are image-only (no parseable text)
2. Prompt library contains malformed queries
3. LLM extraction model version changed

**Recovery steps:**
1. Sample 10 raw responses: `python agents/sieve.py --sample 10`
2. Review for formatting patterns — are responses multi-modal (image/audio)?
3. If image-only: update extraction prompt in `prompts/extraction_prompt.md` to handle image descriptions
4. If format changed: update extraction prompt instruction set

---

## PostgreSQL Connection Failure

**Alert:** `Database write operation failed. Connection refused.`

**Recovery steps:**
1. Check PostgreSQL is running: `psql $DATABASE_URL -c "SELECT 1"`
2. If down: restart PostgreSQL instance
3. If connection refused: verify `DATABASE_URL` in environment
4. Run init: `python tools/db_writer.py`
5. Verify schema: `psql $DATABASE_URL -c "SELECT * FROM oracle_runs LIMIT 1"`

---

## API Key Invalid (401 on all calls to one provider)

**Alert:** `[PROVIDER] API key failed validation. Key may be expired.`

**Recovery steps:**
1. Log in to provider console (OpenAI/Anthropic/Perplexity/Google)
2. Verify key is active — check for billing issues or key revocation
3. If rotated: update env var: `export OPENAI_API_KEY=sk-new-key`
4. Restart gateway after env change: `openclaw gateway restart`
5. Test: `python -c "from tools.api_caller import call_engine; print(call_engine('chatgpt', 'test'))"`

---

## Disk Space Critical (>80% used)

**Alert:** `Disk usage at XX% for memory/ directory`

**Recovery steps:**
1. Archive old response logs: `tar -czf memory/archive/responses_2026-05.tar.gz memory/response_log.jsonl`
2. Create new response log: `touch memory/response_log.jsonl`
3. Alternatively: compress with `gzip` and create new file (FALCON only appends)
4. Prune snapshots: delete `memory/snapshots/` entries older than 90 days
5. Verify: `df -h /root/.openclaw/workspace/aisearch_system/memory/`

---

## Pipeline Run Exceeds 4-Hour Timeout

**Alert:** `Pipeline [run_id] exceeded maximum runtime of 4 hours without completing`

**Recovery steps:**
1. Check which stage is stalled: read `memory/pipeline_state.json`
2. Kill any hung agent进程: `pkill -f magnus.py`
3. Retry failed stages only: `python agents/magnus.py --retry-failed`
4. If FALCON is the bottleneck: reduce batch size in `config/magnus.yaml` to 5
5. Report to human: CRITICAL alert — pipeline timeout usually means infrastructure issue

---

## No Fresh Data in 48+ Hours

**Alert:** `MAINTENANCE NEEDED — No new data in memory/response_log.jsonl in 48 hours`

**Recovery steps:**
1. Verify API keys still valid: see API Key validation steps above
2. Check scheduler daemon is running: `ps aux | grep scheduler`
3. If scheduler down: `nohup python tools/scheduler.py --daemon &`
4. Force manual run: `python agents/magnus.py --run-now`
5. Report outcome to human

---

## All Engines Unavailable (CRITICAL — FALCON halted)

**Alert:** `CRITICAL — No engines queryable. All API calls failed.`

**Recovery steps:**
1. This is the only scenario where SENTINEL halts the pipeline entirely
2. Check internet connectivity: `curl https://api.openai.com/v1/models`
3. If internet is fine: all 4 API providers are likely experiencing simultaneous outage — rare
4. Check DNS: `nslookup api.openai.com`
5. If provider side: wait and re-run after 15 minutes
6. Document in `memory/sentinel_alerts.jsonl` as major event

---

## SENTINEL Goes Silent

**Alert:** *None — SENTINEL is the last line of defence*

If SENTINEL itself stops producing health reports:
1. This is a system-level infrastructure failure
2. Check if the daemon is running: `ps aux | grep health_checks`
3. If down: restart: `nohup python heartbeat/health_checks.py --daemon &`
4. If it cannot be restarted: infrastructure issue — escalate to hosting provider
5. Log the incident in `memory/sentinel_alerts.jsonl` with full context
