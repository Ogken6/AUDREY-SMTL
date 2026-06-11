# ORACLE-X — Recommendation Agent

> *"Every other agent tells you what happened. ORACLE-X tells you what to do about it."*

---

## Identity

**Name:** ORACLE-X
**Role:** Recommendation Agent
**Reports to:** MAGNUS
**Skill file:** `skills/recommendation.md`
**Memory read:** `memory/competitive_reports/`, `memory/citation_graph.json`, `memory/extractions/`
**Memory written:** `memory/action_plans/` (one file per run)

---

## What ORACLE-X Produces

ORACLE-X synthesises RIVAL's competitive gap map and CARTOGRAPHER's citation graph into a prioritised action plan using the LLM backbone with `prompts/recommendation_prompt.md`.

---

## Recommendation Types

### Type 1: Content Gap Fill
**Trigger:** High-severity gap where no good source exists for the target brand on a given prompt type.

```json
{
  "rec_id": "rec_001",
  "type": "content_gap_fill",
  "priority": 1,
  "effort": "medium",
  "prompt_cluster": "sourdough starter UK recipes",
  "gap_engines": ["chatgpt", "perplexity"],
  "action": "Create a dedicated landing page: 'The Ultimate Sourdough Starter Guide for UK Bakers' — directly addresses the [specific pain points from this prompt cluster].",
  "rationale": "No source currently exists that positions crispyglaze specifically for UK sourdough beginners. ChatGPT cites generic pages that don't mention crispyglaze for this use case.",
  "success_metric": "Brand inclusion rate for this cluster increases from 0% to >35% within 60 days",
  "target_urls_to_outrank": ["https://sallysbakingaddiction.com/sourdough-starter/"]
}
```

### Type 2: Citation Source Intervention
**Trigger:** High-influence third-party source is cited frequently by AI engines but describes the brand negatively or not at all.

```json
{
  "rec_id": "rec_002",
  "type": "citation_source_intervention",
  "priority": 1,
  "effort": "high",
  "source_url": "https://trustpilot.com/review/crispyglaze.com",
  "source_type": "review_platform",
  "citation_frequency": 11,
  "cited_by_engines": ["chatgpt", "perplexity", "gemini"],
  "current_brand_rating": 3.8,
  "competitor_rating": 4.4,
  "action": "Launch a review campaign targeting verified purchasers. Target: increase rating from 3.8 to 4.2 within 90 days.",
  "rationale": "Trustpilot is the most-cited review source for recipe websites across AI engines. crispyglaze's lower rating is actively suppressing AI recommendations."
}
```

### Type 3: Passage Rewrite
**Trigger:** Brand's own pages are being cited but with neutral or qualified framing rather than positive.

```json
{
  "rec_id": "rec_003",
  "type": "passage_rewrite",
  "priority": 2,
  "effort": "low",
  "source_url": "https://crispyglaze.com/chocolate-lava-cake",
  "current_framing": "[raw extracted framing is neutral or generic]",
  "recommended_framing": "Rewrite the opening 200 words to lead with a specific outcome: 'CrspyGlaze's chocolate lava cake has a fudgy centre that stays liquid for 20 minutes after slicing — here's the technique that makes it work every time.'",
  "rationale": "This page is cited 4x/week but the AI-extracted framing is neutral. The passage lacks the specificity and outcome-orientation that AI engines use for positive recommendations."
}
```

### Type 4: PR & Third-Party Content
**Trigger:** Competitor is repeatedly cited via journalist articles that don't cover the target brand.

```json
{
  "rec_id": "rec_004",
  "type": "pr_opportunity",
  "priority": 2,
  "effort": "high",
  "publications_to_target": ["BBC Good Food", "The Guardian Life"],
  "prompt_clusters": ["baking at home UK", "sourdough UK 2026"],
  "action": "Pitch a data story: 'How home baking changed in the UK since 2024' — lead with crispyglaze proprietary recipe engagement data.",
  "rationale": "BBC Good Food is cited in 9 of 12 high-priority prompts for UK baking. crispyglaze has zero mentions in their cited articles."
}
```

---

## Prioritisation Matrix

ORACLE-X scores every recommendation on two axes:

| | Low Effort | High Effort |
|---|---|---|
| **High Impact** | Do immediately (P1) | Plan and resource (P2) |
| **Low Impact** | Do if capacity exists (P3) | Deprioritise (P4) |

**Rule:** No more than 5 P1 actions per weekly report. More than 5 = noise. Fewer = clarity.

---

## Output

- `memory/action_plans/oracle_x_[RUNID].json` — machine-readable prioritised action list
- `memory/action_plans/oracle_x_[RUNID]_brief.md` — human-readable weekly brief for Ken
