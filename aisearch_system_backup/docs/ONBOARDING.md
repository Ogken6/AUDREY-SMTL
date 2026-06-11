# ONBOARDING.md — Setting Up a New Brand in ORACLE

---

## Step 1: Configure the Brand

Copy the brand config template:
```bash
cp config/brands.yaml config/brands_local.yaml
```

Edit `config/brands_local.yaml`:
- Set `canonical_name` and all `name_variants` (be exhaustive — AI engines use many forms)
- List all `owned_domains`
- Add all known `competitors` with their name variants and domains
- Set `target_personas` — these inform SCOUT's prompt generation
- List the most relevant `subreddits` for your category

## Step 2: Build the Entity Registry

Run the entity registry initialiser:
```bash
python tools/setup_entity_registry.py --brand=crispyglaze
```

Review the output at `memory/entity_registry.json` and add any missing name variants manually.

## Step 3: Set API Keys

Create a `.env` file (gitignored):
```bash
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
GOOGLE_AI_API_KEY=...
PERPLEXITY_API_KEY=...
PROXY_API_KEY=...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SLACK_WEBHOOK_URL=...
```

## Step 4: Initialise the Database
```bash
psql $DATABASE_URL -f dashboard/schema.sql
```

## Step 5: Run SCOUT to Build the Initial Prompt Library
```bash
python agents/scout.py --brand=crispyglaze --initial-build
```

Review the generated prompt library:
```bash
python tools/prompt_reviewer.py --brand=crispyglaze
```

Manually add any anchor prompts that are critical to your category. Set `"anchor": true` in the JSON.

## Step 6: Start SENTINEL
```bash
python heartbeat/health_checks.py --daemon --brand=crispyglaze
```

Confirm SENTINEL is running and reporting to Slack before proceeding.

## Step 7: Run the First Pipeline
```bash
python agents/magnus.py --run-now --brand=crispyglaze
```

First run takes 60–90 minutes. Monitor progress:
```bash
tail -f logs/magnus.log
```

## Step 8: Review First Results

After the pipeline completes:
```bash
python tools/run_report.py --run-id=$(cat memory/pipeline_state.json | jq -r .run_id)
```

Check:
- Did all engines return responses?
- Is extraction confidence averaging above 0.75?
- Are competitor names being detected correctly?
- Are citation URLs being fetched successfully?

Adjust entity registry if brand or competitor names aren't being detected correctly.

## Step 9: Establish Baselines

Run the pipeline for **5–7 days before acting on any recommendations**. ORACLE-X needs baseline data to generate meaningful recommendations. Don't optimise against day-1 data.

---

# TROUBLESHOOTING.md — Common Failure Modes

---

## "Brand not being detected in responses where it clearly appears"

**Cause:** Name variant missing from entity registry
**Fix:** Add the variant to `memory/entity_registry.json` → `target_brand.variants`
**Prevention:** Run `python tools/variant_scanner.py` after brand config changes

---

## "Extraction confidence consistently below 0.70"

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

## "Google AIO returning 0 results"

**Cause:** AIO CSS selector has changed, or AIO not triggering for these prompts
**Fix:** See `heartbeat/recovery_playbook.md#FAIL-01`
**Quick check:** Run `python tools/browser_agent.py --test --engine=google_aio --prompt="best recipe websites UK"`

---

## "Citation graph not growing — same sources every run"

**Cause:** Prompt library too narrow; AI engines returning cached/consistent answers
**Fix:**
1. Add more prompt variety (especially problem_framing and validation intents)
2. Test prompts from different geographic regions
3. Check if CARTOGRAPHER is skipping sources due to cache (48-hour cache may be too long — reduce to 24h in `config/system.yaml`)

---

## "RIVAL showing competitor with 90%+ SoV — seems too high"

**Cause:** Usually a prompt cluster that's too narrow and competitor-specific
**Fix:**
1. Check which prompts are driving the high competitor SoV
2. If prompts are "comparison" type (e.g. "vs [Competitor]"), this is expected
3. If prompts are generic discovery prompts, this is a genuine gap — prioritise for ORACLE-X

---

## "ORACLE-X recommendations are too vague"

**Cause:** Insufficient extraction data for the recommendation engine to work with
**Fix:**
1. Ensure at least 7 days of pipeline data before running ORACLE-X
2. Check that CARTOGRAPHER is successfully fetching citation source content
3. Verify gap map has at least 10 gaps with severity scores — small gap maps produce generic recommendations

---

## "Pipeline taking > 4 hours — timing out"

**Cause:** Usually proxy latency issues or engine rate limiting
**Fix:**
1. Check proxy pool health: `python tools/proxy_manager.py --health`
2. Check FALCON logs for rate limit events
3. Reduce concurrent query batch size in `config/system.yaml`
4. Consider reducing prompt library size temporarily

---

## "SENTINEL alerts firing constantly — alert fatigue"

**Cause:** Thresholds set too aggressively for the system's actual variance
**Fix:**
1. Review `config/thresholds.yaml` — are thresholds calibrated for your actual data?
2. After 14 days of operation, run `python tools/threshold_calibrator.py` to auto-suggest thresholds based on observed variance
3. Check if a specific agent is repeatedly triggering — may indicate a genuine persistent issue masking as noise
