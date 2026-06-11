# TROUBLESHOOTING.md — Common Failure Modes

---

## Brand not being detected in responses where it clearly appears

**Cause:** Name variant missing from entity registry
**Fix:** Add the variant to `memory/entity_registry.json` → `brands.crispyglaze.name_variants`
**Prevention:** Run `python tools/variant_scanner.py` after brand config changes

---

## Extraction confidence consistently below 0.70

**Cause:** Usually one of:
1. Responses are very short and non-substantive (low-quality prompts)
2. Engine is returning refusals or caveats instead of recommendations
3. Brand name is ambiguous (also a common English word)

**Fix:**
1. Review low-confidence responses in extraction logs — identify the pattern
2. For case 1: Retire weak prompts, add more specific prompts
3. For case 2: Flag the engine; check if it's a known model behaviour
4. For case 3: Add more specific brand identifiers to entity registry

---

## Google AIO returning 0 results

**Cause:** AIO CSS selector has changed, or AIO not triggering for these prompts
**Fix:** See `heartbeat/recovery_playbook.md#FAIL-01`
**Quick check:** `python tools/browser_agent.py --test --engine=google_aio --prompt="best recipe websites UK"`

---

## Citation graph not growing — same sources every run

**Cause:** Prompt library too narrow; AI engines returning cached/consistent answers
**Fix:**
1. Add more prompt variety (especially problem_framing and validation intents)
2. Test prompts from different geographic regions
3. Reduce cache TTL in `config/system.yaml` if CARTOGRAPHER is reusing stale cached content

---

## RIVAL showing competitor with 90%+ SoV — seems too high

**Cause:** Usually a prompt cluster that's too narrow and competitor-specific
**Fix:**
1. Check which prompts are driving the high competitor SoV
2. If prompts are "comparison" type (e.g. "vs [Competitor]"), this is expected
3. If prompts are generic discovery prompts, this is a genuine gap — prioritise for ORACLE-X

---

## ORACLE-X recommendations are too vague

**Cause:** Insufficient extraction data for the recommendation engine to work with
**Fix:**
1. Ensure at least 7 days of pipeline data before running ORACLE-X
2. Check that CARTOGRAPHER is successfully fetching citation source content
3. Verify gap map has at least 10 gaps with severity scores — small gap maps produce generic recommendations

---

## Pipeline taking > 4 hours — timing out

**Cause:** Usually proxy latency issues or engine rate limiting
**Fix:**
1. Check proxy pool health: `python tools/proxy_manager.py --health`
2. Check FALCON logs for rate limit events
3. Reduce concurrent query batch size in `config/system.yaml`
4. Consider reducing prompt library size temporarily

---

## SENTINEL alerts firing constantly — alert fatigue

**Cause:** Thresholds set too aggressively for the system's actual variance
**Fix:**
1. Review `config/thresholds.yaml` — are thresholds calibrated for your actual data?
2. After 14 days of operation, run `python tools/threshold_calibrator.py`
3. Check if a specific agent is repeatedly triggering — may indicate a genuine persistent issue masking as noise

---

## All browser engines returning personalisation warnings

**Cause:** Browser sessions not being cleared properly between queries
**Fix:**
1. Verify proxy is working — personalisation often indicates the request is coming from the same session as a previous query
2. Force new Playwright context: `python tools/browser_agent.py --fresh-session --engine=copilot`
3. Check that `proxy_manager.py` is rotating IPs correctly

---

## Perplexity returning no citations field

**Cause:** Perplexity API model may have changed; verify `citations_field` in `config/engines.yaml`
**Fix:**
1. Check Perplexity API response format: `python -c "from tools.api_caller import APICaller; print(APICaller().query_engine('perplexity', 'test'))"`
2. If citations field name changed, update `config/engines.yaml` → `perplexity.citations_field`

---

## Database writes failing after pipeline run

**Cause:** Usually PostgreSQL connection pool exhaustion or disk full
**Fix:**
1. `psql $DATABASE_URL -c "SELECT 1"` — test connection
2. Check disk: `df -h` on the database server
3. If pool exhausted: restart connection: `python tools/db_writer.py` (auto-reconnects)
4. Verify MAGNUS is writing run summary at end of every run — if not, check error logs

---

## Prompt library has duplicate prompts despite dedup

**Cause:** Semantic dedup threshold too high (0.92 allows near-duplicates)
**Fix:**
1. Lower threshold in `skills/prompt_generation.md`: cosine similarity > 0.85 instead of 0.92
2. Re-run dedup: `python agents/scout.py --brand=crispyglaze --dedup-only`
3. Manually review `memory/prompt_library.json` for obvious duplicates

---

## DISK SPACE CRITICAL — response log growing too fast

**Cause:** Full pipeline runs without archiving; response_log.jsonl growing unbounded
**Fix:**
1. Immediate: `tar -czf memory/snapshots/responses_2026-05.tar.gz -C memory response_log.jsonl && cp /dev/null memory/response_log.jsonl`
2. Long term: `config/thresholds.yaml` → `storage.archive_after_days` — ensure set to 90 days max
3. Set up a cron job to run `python tools/archive_responses.py` weekly
