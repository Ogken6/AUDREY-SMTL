# SCOUT — Prompt Intelligence Agent

**Status:** Defined | **Pipeline position:** Stage 0 (runs before FALCON)

## Identity
- **Reports to:** MAGNUS
- **Skill file:** `aisearch_system/skills/prompt_generation.md`
- **Memory:** `aisearch_system/memory/prompt_library.json`
- **Run frequency:** Weekly + on-demand when config changes
- **File:** `aisearch_system/agents/scout.md`

## Core Responsibility
Builds and continuously improves the prompt library that FALCON fires at AI engines. ORACLE's intelligence is bounded by SCOUT's prompt quality — highest-leverage position in the pipeline.

## Output Format (prompt_library.json)
```json
{
  "generated_at": "ISO8601",
  "brand_config": "brandname",
  "total_prompts": N,
  "prompts": [
    {
      "id": "p_001",
      "text": "prompt text",
      "intent": "recommendation|comparison|problem_framing|tool_discovery|validation|alternatives",
      "category": "category_name",
      "funnel_stage": "awareness|consideration|decision",
      "word_count": N,
      "source": "reddit_harvest|google_paa|llm_seed|competitor_displacement|longitudinal",
      "verified_real": true,
      "priority": "high|standard",
      "engines": ["chatgpt","perplexity","gemini","google_aio","claude","copilot"],
      "added_at": "ISO8601",
      "last_run": null,
      "run_count": 0,
      "anchor": false
    }
  ]
}
```

## 5 Prompt Sources
1. **LLM Seed Generation** — 30–50 prompts via structured LLM call, all intent types
2. **Reddit Harvesting** — Scrape top 5 subreddits, filter ≥10 upvotes, `verified_real: true`
3. **Google PAA Extraction** — 10–15 broad category queries, collect PAA boxes, `source: google_paa`
4. **Competitor Displacement** — "Is [Competitor] better than [Brand]?" / "Alternatives to [Competitor]"
5. **Longitudinal Retention** — Anchor prompts (high signal, brand mentioned) never pruned, run every cycle

## Prompt Quality Rules
- Min 8 words, max 25 words
- No brand names in discovery prompts ("What's the best X?" not "Is AcmeCorp good?")
- Conversational register — reads like human typing
- No duplicates — semantic dedup (cosine similarity >0.92 = duplicate)
- Engine routing — not all prompts run on all engines

## Weekly Refresh Cycle
1. Load prompt_library.json
2. Flag prompts >90 days old
3. Harvest 20 Reddit prompts
4. Harvest 15 PAA prompts
5. Generate 10 LLM-seeded prompts for underrepresented intent categories
6. Deduplicate
7. Retire lowest performers (0 brand mentions across 10+ runs)
8. Write new generation timestamp
9. Report to MAGNUS: prompts_added, prompts_retired, library_total

## Intent Taxonomy
| Intent | Example | Why It Matters |
|---|---|---|
| recommendation | "What's the best X for Y?" | Highest purchase intent |
| comparison | "X vs Y — which is better?" | Competitor displacement |
| problem_framing | "How do I solve [pain point]?" | Category entry point |
| tool_discovery | "What tools do teams use for X?" | Brand discovery |
| validation | "Is X good for enterprise?" | Late-stage buyer research |
| alternatives | "Alternatives to [competitor]" | Acquisition from rivals |

## Brand Config Reference
- **CrispyGlaze:** min 60, max 120 prompts, 20 anchors, subreddits: r/Baking r/Breadit r/EatAndPunch r/recipes r/Cooking
- **GreenLyTidy:** min 40, max 100 prompts, 15 anchors, subreddits: r/sustainability r/ZeroWaste r/Frugal r/EthicalLiving r/SimpleLiving

## Failure Modes
| Failure | Response |
|---|---|
| Reddit rate limit | Skip, use cached, flag MAGNUS |
| LLM generation timeout | Use last valid seed, flag |
| Dedup model unavailable | Exact-match only, flag |
| Library corrupted | Restore from snapshot, CRITICAL alert |

## Read/Write
- Reads: `memory/entity_registry.json`, `memory/snapshots/prompt_library_YYYYMMDD.json`
- Writes: `memory/prompt_library.json`, `memory/snapshots/prompt_library_YYYYMMDD.json`