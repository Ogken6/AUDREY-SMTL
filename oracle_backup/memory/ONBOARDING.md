# ONBOARDING.md — Setting Up a New Brand in ORACLE

**File:** `aisearch_system/docs/ONBOARDING.md`

## Step 1: Configure the Brand
```bash
cp config/brands.yaml config/brands_local.yaml
# Edit brands_local.yaml:
# - canonical_name + all name_variants (be exhaustive)
# - owned_domains
# - competitors with name variants and domains
# - target_personas
# - relevant subreddits
```

## Step 2: Build the Entity Registry
```bash
python tools/setup_entity_registry.py --brand=BRAND_SLUG
# Review output at memory/entity_registry.json
# Add missing name variants manually
```

## Step 3: Set API Keys
```bash
# Create .env (gitignored):
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
GOOGLE_AI_API_KEY=...
PERPLEXITY_API_KEY=...
PROXY_API_KEY=...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SLACK_WEBHOOK_URL=...
```

## Step 4: Initialise Database
```bash
psql $DATABASE_URL -f dashboard/schema.sql
```

## Step 5: Run SCOUT — Build Initial Prompt Library
```bash
python agents/scout.py --brand=BRAND_SLUG --initial-build
# Review: python tools/prompt_reviewer.py --brand=BRAND_SLUG
# Manually add anchor prompts — set "anchor": true
```

## Step 6: Start SENTINEL
```bash
python heartbeat/health_checks.py --daemon --brand=BRAND_SLUG
# Confirm reporting to Slack before proceeding
```

## Step 7: Run First Pipeline
```bash
python agents/magnus.py --run-now --brand=BRAND_SLUG
# First run: 60–90 minutes
# Monitor: tail -f logs/magnus.log
```

## Step 8: Review First Results
```bash
python tools/run_report.py --run-id=$(cat memory/pipeline_state.json | jq -r .run_id)
```
Check:
- All engines returning responses?
- Extraction confidence avg > 0.75?
- Competitor names detected correctly?
- Citation URLs fetched successfully?
- Adjust entity registry if detection is failing

## Step 9: Establish Baselines
**Run pipeline for 5–7 days before acting on recommendations.** ORACLE-X needs baseline data. Don't optimise against day-1 data.