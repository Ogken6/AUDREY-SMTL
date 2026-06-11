# MEMORY.md — ORACLE Memory System

> *"Agents that forget are agents that start over. ORACLE never starts over."*

---

## Active Brand: CrispyGlaze

**Domain:** crispyglaze.com | **Founded:** 2025 | **Base:** Columbia, Maryland, USA
**Primary keyword:** "simple comfort food recipes" | **Co-primary:** "easy comfort food recipes"
Both tracked independently with equal priority. Displacement on either = CRITICAL alert.

**Team:** Mira (Thai-American founder), Stacey, Shola, Elena
**Target markets:** United States (primary) · Canada (secondary)
**Brand voice:** Warm, real, multicultural, accessible. Food is connection, not performance.
**Key differentiator:** Four-woman multicultural team bringing genuine global flavor to simple and easy comfort food.

**Recipe categories:** Breakfast Ideas · Appetizers and Party Foods · Soup and Chowder · Easy Homemade Breads · Easy Dessert Recipes

**Cuisines:** Brazilian · Chinese · French · German · Greek · Italian · Japanese · Korean · Mexican · Spanish · Thai · Turkish

**Competitor tiers:**
- CRITICAL: AllRecipes (122M+ traffic, DR 95), Simply Recipes (19–21M, DR 80)
- HIGH: Food Network, Tastes Better From Scratch, Spend With Pennies, Damn Delicious, The Cozy Cook (closest direct competitor)
- MEDIUM: The Kitchn, The Country Cook, Delish, A Cozy Kitchen, Budget Bytes, Taste of Home
- Canada HIGH: Rock Recipes (NL), The Recipe Rebel, Closet Cooking (Toronto)

**RIVAL priority watch:** The Cozy Cook · Damn Delicious · Tastes Better From Scratch · Rock Recipes · Closet Cooking

**Perplexity:** DISABLED — enable when subscribed. Activate: add key to .env + set `perplexity.enabled: true` in engines.yaml. Matters because ~56% of AI referral traffic + ~40% of citations from Reddit.

**Run mode:** BASELINE BUILD — do not act on ORACLE-X recommendations until 7 days of data collected. First meaningful recommendations: Day 8.

---

## System Overview

ORACLE's memory system is the shared persistent layer that all agents read from and write to. It is the only way agents communicate state — no agent calls another agent directly. Every handoff is mediated by memory.

Memory in ORACLE has four types:

| Type | Description | Examples |
|---|---|---|
| **Working memory** | Current pipeline state, live job queues | `pipeline_state.json` |
| **Response memory** | Raw and extracted AI engine outputs | `response_log.jsonl`, `extractions/` |
| **Knowledge memory** | Accumulated intelligence about the brand, competitors, citations | `citation_graph.json`, `entity_registry.json` |
| **Action memory** | Historical recommendations and their outcomes | `action_plans/` |

---

## Memory Files Reference

### `memory/pipeline_state.json`
**Owner:** MAGNUS (read/write) | **Other readers:** SENTINEL
**Purpose:** Real-time pipeline execution state. Updated after every stage transition.
**Schema:** See `memory/MAGNUS.md`

---

### `memory/prompt_library.json`
**Owner:** SCOUT (read/write) | **Other readers:** FALCON, MAGNUS
**Snapshot:** Daily copy to `memory/snapshots/prompt_library_YYYYMMDD.json`

```json
{
  "generated_at": "ISO8601",
  "brand_config": "string — matches brands.yaml key",
  "total_prompts": "integer",
  "anchor_count": "integer — prompts that never get retired",
  "prompts": [
    {
      "id": "p_NNN",
      "text": "string",
      "intent": "recommendation|comparison|problem_framing|tool_discovery|validation|alternatives",
      "category": "string",
      "funnel_stage": "awareness|consideration|decision",
      "word_count": "integer",
      "source": "llm_generated|reddit_harvest|google_paa|human_added",
      "verified_real": "boolean",
      "priority": "high|standard|low",
      "anchor": "boolean — true if this prompt never gets retired",
      "engines": ["array of engine IDs"],
      "added_at": "ISO8601",
      "last_run": "ISO8601 or null",
      "run_count": "integer",
      "lifetime_brand_mention_count": "integer",
      "lifetime_brand_recommendation_count": "integer"
    }
  ]
}
```

---

### `memory/response_log.jsonl`
**Owner:** FALCON (append-only write) | **Other readers:** SIEVE, SENTINEL
**Format:** JSONL — one JSON object per line, never overwritten
**Snapshot:** Daily copy to `memory/snapshots/responses_YYYYMMDD.jsonl`

This is ORACLE's most important data store. Immutable record of every AI engine response ever captured. Nothing is ever deleted.

```json
{
  "response_id": "resp_YYYYMMDD_pNNN_engine",
  "run_id": "run_YYYYMMDD_HHMMSS",
  "prompt_id": "p_NNN",
  "prompt_text": "string",
  "engine": "chatgpt|perplexity|google_aio|google_aim|gemini|claude|copilot",
  "model_version": "string",
  "captured_at": "ISO8601",
  "region": "us-east|eu-west|apac",
  "session_id": "string",
  "raw_response": "string — FULL unmodified response text",
  "cited_urls": ["array of URLs"],
  "response_length_chars": "integer",
  "latency_ms": "integer",
  "capture_method": "api|browser",
  "screenshot_path": "string or null",
  "aio_present": "boolean or null — only for google_aio",
  "personalisation_detected": "boolean",
  "personalisation_flags": ["array of flag descriptions"],
  "status": "success|timeout|error|rate_limited",
  "error": "string or null",
  "data_quality_flags": ["array of flag strings"]
}
```

---

### `memory/extractions/run_YYYYMMDD.json`
**Owner:** SIEVE (write) | **Other readers:** CARTOGRAPHER, RIVAL, ORACLE-X
**One file per pipeline run**

```json
{
  "run_id": "string",
  "extracted_at": "ISO8601",
  "total_responses_processed": "integer",
  "total_extraction_failures": "integer",
  "avg_confidence": "float",
  "low_confidence_count": "integer",
  "extractions": [
    {
      "response_id": "string",
      "prompt_id": "string",
      "engine": "string",
      "brand_present": "boolean",
      "brand_position_rank": "integer or null",
      "brand_recommendation_position": "integer or null",
      "brand_sentiment": "strong_recommend|recommend|neutral|qualified|negative|absent",
      "brand_sentiment_confidence": "float 0-1",
      "brand_sentiment_evidence": "string — quoted passage from response",
      "brand_qualifiers": ["array of qualifier strings"],
      "entities": [
        {
          "name": "string",
          "canonical_name": "string",
          "type": "brand|product|person|organisation",
          "is_target_brand": "boolean",
          "is_tracked_competitor": "boolean",
          "mention_position": "integer",
          "is_recommended": "boolean",
          "is_cited": "boolean",
          "qualifier": "string or null"
        }
      ],
      "cited_urls": ["array"],
      "cited_domain_types": ["array of source_type strings"],
      "competitor_count_in_response": "integer",
      "competitors_ranked_above_brand": ["array of competitor names"],
      "extraction_confidence": "float 0-1",
      "extraction_flags": ["array of flag strings"]
    }
  ]
}
```

---

### `memory/citation_graph.json`
**Owner:** CARTOGRAPHER (read/write) | **Other readers:** RIVAL, ORACLE-X, SENTINEL
**Updated:** Every 6 hours

```json
{
  "updated_at": "ISO8601",
  "brand": "string",
  "total_unique_sources": "integer",
  "nodes": [
    {
      "url": "string",
      "domain": "string",
      "source_type": "brand_owned|tech_media|review_platform|ugc_forum|encyclopedia|analyst|competitor_owned|unknown",
      "domain_authority": "integer 0-100",
      "influence_score": "float 0-100",
      "brand_mentioned": "boolean",
      "brand_sentiment": "positive|neutral|negative|not_mentioned",
      "brand_content_snippet": "string — key brand-relevant passage",
      "competitor_mentions": ["array of competitor names"],
      "content_age_days": "integer",
      "cited_by_engines": ["array of engine IDs"],
      "citation_frequency": "integer — citations in last 30 days",
      "citation_frequency_trend": "increasing|stable|decreasing",
      "last_fetched": "ISO8601",
      "fetch_status": "success|blocked|not_found|timeout"
    }
  ],
  "edges": [
    {
      "prompt_id": "string",
      "engine": "string",
      "response_id": "string",
      "source_url": "string",
      "brand_mentioned_in_source": "boolean",
      "brand_cited_in_answer": "boolean",
      "cited_at": "ISO8601"
    }
  ]
}
```

---

### `memory/entity_registry.json`
**Owner:** Human operator (initial) + RIVAL (updates competitor discoveries)
**Other readers:** SCOUT, SIEVE, CARTOGRAPHER
**Updated:** When new competitors detected by RIVAL or manually by Ken

```json
{
  "updated_at": "ISO8601",
  "target_brand": {
    "canonical": "string",
    "variants": ["array of name variants"],
    "domains": ["array of owned domains"],
    "products": ["array of product names"],
    "personas": ["array of target customer descriptions"]
  },
  "competitors": [
    {
      "canonical": "string",
      "variants": ["array"],
      "domains": ["array"],
      "tier": "primary|secondary|emerging",
      "added_at": "ISO8601",
      "added_by": "human|rival_agent"
    }
  ],
  "category_terms": ["array of category keywords"],
  "excluded_terms": ["array of terms to ignore in extraction"]
}
```

---

### `memory/competitive_reports/report_YYYYMMDD.json`
**Owner:** RIVAL (write) | **Other readers:** ORACLE-X, Ken

Full schema: see `memory/RIVAL.md` — Report Schema section.

---

### `memory/action_plans/plan_YYYYMMDD.json`
**Owner:** ORACLE-X (write) | **Other readers:** Ken

```json
{
  "plan_id": "string",
  "generated_at": "ISO8601",
  "based_on_run": "string — run_id",
  "brand": "string",
  "executive_summary": "string — 3–5 sentence plain-language summary",
  "key_metrics": {
    "overall_brand_inclusion_rate": "float",
    "week_over_week_change": "float",
    "high_severity_gaps": "integer",
    "displacement_events_this_week": "integer"
  },
  "recommendations": [
    {
      "rec_id": "string",
      "type": "content_gap_fill|citation_source_intervention|passage_rewrite|pr_opportunity|entity_correction|review_campaign",
      "priority": "1|2|3|4",
      "effort": "low|medium|high",
      "effort_hours_estimate": "integer",
      "action": "string — specific, concrete",
      "rationale": "string — gap data, prompt cluster, engine, citation source",
      "success_metric": "string — measure and timeline",
      "target_urls": ["array"],
      "target_publications": ["array"],
      "gap_references": ["array of gap_ids"]
    }
  ],
  "full_gap_map_ref": "string — path to competitive report",
  "next_review_date": "ISO8601"
}
```

---

## Memory Integrity Rules

1. **`response_log.jsonl` is append-only.** No agent ever modifies or deletes existing lines.
2. **All memory files are snapshotted daily** before any write operations.
3. **SENTINEL monitors all file modification timestamps** — unexpected silence triggers alerts.
4. **Schema validation runs on every write** — malformed records are rejected and logged, not silently stored.
5. **Sensitive data (API keys, proxy credentials) never appears in memory files** — only in environment variables.

---

## Four Memory Types Summary

| Type | What it holds | Key files |
|---|---|---|
| **Working** | Pipeline state, job queues | `pipeline_state.json` |
| **Response** | Raw + extracted AI outputs | `response_log.jsonl`, `extractions/` |
| **Knowledge** | Brand, competitor, citation intelligence | `citation_graph.json`, `entity_registry.json`, `prompt_library.json` |
| **Action** | Historical recommendations + outcomes | `action_plans/` |

---

## Principles

1. **Raw data is sacred** — `response_log.jsonl` is append-only, never overwritten
2. **Every data point traces to a recommendation** — ORACLE-X delivers max 5 P1 per weekly report
3. **No acting on Day 1 data** — 7-day baseline before recommendations
4. **SENTINEL is independent** — MAGNUS cannot suppress SENTINEL alerts
5. **Both keywords tracked independently** — "simple" and "easy" each have their own SoV, displacement alerts, and anchor prompts
6. **Perplexity citation patterns matter** — Reddit is the primary citation source for comfort food queries

---

## Git Log (Oracle Memory Workspace)

```
d90a25a load CrispyGlaze brand spawn document — full config, 30 anchors
7a8dfe5 add ONBOARDING.md and TROUBLESHOOTING.md — setup guide + 7 failure modes
89a6276 add DASHBOARD.md — 6 views, full DB schema, all API endpoints
792e4f4 BRANDS.md: clarify acme_corp is doc placeholder only
484ba6d add SYSTEM.md, THRESHOLDS.md, BRANDS.md — full system configuration
a1f2cad add HEARTBEAT.md — full heartbeat system design
988e1dd add TOOLS.md — full tool registry with usage examples
430cfff update full MEMORY.md with complete memory system spec
5c88cb0 store all 7 ORACLE skills in memory
27a0d3c update SIEVE, CARTOGRAPHER, RIVAL, ORACLE-X from source defs
abc38c5 full agent roster documented in memory
6a02ef6 Oracle bootstrap: identity, memory, user profile established
``` |