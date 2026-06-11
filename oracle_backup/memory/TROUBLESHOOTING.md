# TROUBLESHOOTING.md — Common Failure Modes

**File:** `aisearch_system/docs/TROUBLESHOOTING.md`

## Brand Not Detected in Responses
**Cause:** Name variant missing from entity registry
**Fix:** Add variant to `memory/entity_registry.json` → `target_brand.variants`
**Prevention:** Run `python tools/variant_scanner.py` after brand config changes

---

## Extraction Confidence Consistently Below 0.70
**Causes:**
1. Short/non-substantive responses (weak prompts)
2. Engine returning refusals/caveats instead of recommendations
3. Brand name is ambiguous common word

**Fix:**
1. Review low-confidence responses — identify the pattern
2. Case 1: Retire weak prompts, add more specific ones
3. Case 2: Flag engine; check known model behaviour
4. Case 3: Add more specific brand identifiers to entity registry

---

## Google AIO Returning 0 Results
**Cause:** CSS selector changed, or AIO not triggering for these prompts
**Fix:** See `memory/HEARTBEAT.md` → FAIL-01
**Quick check:**
```bash
python tools/browser_agent.py --test --engine=google_aio --prompt="best project management software"
```

---

## Citation Graph Not Growing — Same Sources Every Run
**Cause:** Prompt library too narrow; AI engines returning cached answers
**Fix:**
1. Add more prompt variety (problem_framing, validation intents)
2. Test from different geographic regions
3. Check if CARTOGRAPHER skipping sources due to cache — try reducing cache TTL to 24h in `config/system.yaml`

---

## RIVAL Showing Competitor 90%+ SoV — Seems Too High
**Cause:** Usually a narrow, competitor-specific prompt cluster
**Fix:**
1. Check which prompts are driving high competitor SoV
2. "Comparison" type prompts (e.g. "vs [Competitor]") → expected
3. Generic discovery prompts → genuine gap → ORACLE-X priority

---

## ORACLE-X Recommendations Too Vague
**Cause:** Insufficient extraction data for recommendation engine
**Fix:**
1. Ensure at least 7 days of pipeline data before ORACLE-X
2. Check CARTOGRAPHER fetching citation source content successfully
3. Verify gap map has ≥10 gaps with severity scores — small gap maps produce generic recommendations

---

## Pipeline Taking > 4 Hours — Timing Out
**Cause:** Proxy latency issues or engine rate limiting
**Fix:**
1. Check proxy pool health: `python tools/proxy_manager.py --health`
2. Check FALCON logs for rate limit events
3. Reduce concurrent query batch size in `config/system.yaml`
4. Consider temporarily reducing prompt library size

---

## SENTINEL Alert Fatigue
**Cause:** Thresholds too aggressive for system's actual variance
**Fix:**
1. Review `config/thresholds.yaml` — calibrate to actual data variance
2. After 14 days: run `python tools/threshold_calibrator.py` to auto-suggest thresholds
3. Check if specific agent repeatedly triggering — may indicate persistent underlying issue