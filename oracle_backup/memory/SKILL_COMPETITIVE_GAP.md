# SKILL: Competitive Gap Analysis
**Used by:** RIVAL | **Version:** 1.0

## Purpose
Defines how to compute share of voice, gap maps, and displacement events from SIEVE extraction data.

## Share of Voice Calculation
```python
def calculate_sov(brand, prompt_id, engine, time_window_days=7):
    responses = get_responses(prompt_id, engine, time_window_days)
    brand_mentions = sum(1 for r in responses if brand in r.entity_names)
    return brand_mentions / len(responses) if responses else 0
```

Run SoV for:
- Each prompt × engine combination
- Each prompt cluster (grouped by intent type)
- Each engine (aggregate across all prompts)
- Overall (aggregate across all prompts and engines)

## Key Metrics
```
SoV = (responses mentioning target brand) / (total responses for prompt × engine)
Brand Inclusion Rate = (responses where brand is present) / (total responses)
Brand Recommendation Rate = (responses where brand is first or second) / (total responses)
```

## Gap Severity Scoring
```python
def calculate_gap_severity(gap):
    base_score = 0
    base_score += gap.frequency_across_runs * 2
    base_score += len(gap.engines_with_gap) * 15
    base_score += gap.competitor_consistency_rate * 20
    base_score += INTENT_WEIGHTS[gap.prompt_intent] * 10
    if base_score > 70: return "high"
    if base_score > 40: return "medium"
    return "low"
```

## Displacement Event Definition
A displacement event occurs when ALL of these are true:
1. Previous run: brand was present (`brand_present = true`)
2. Current run: brand is absent (`brand_present = false`)
3. AND: a competitor that was not previously present is now present

**Displacement events = highest-priority signals in the system. They represent active brand erosion.**

## Gap Map Entry
```json
{
  "gap_id": "gap_p001_chatgpt_bbcgoodfood",
  "prompt": "...",
  "engine": "chatgpt",
  "competitor_present": "BBC Good Food",
  "competitor_position": 1,
  "target_brand_present": false,
  "gap_severity": "high",
  "frequency_across_runs": 8,
  "citation_source": "https://bbcgoodfood.com/..."
}
```