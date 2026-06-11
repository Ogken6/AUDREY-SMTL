# SKILL: Competitive Gap Analysis
**Used by:** RIVAL
**Version:** 1.0

---

## Purpose
This skill defines how to compute share of voice, gap maps, and displacement events from SIEVE extraction data.

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

## Gap Severity Scoring

```python
def calculate_gap_severity(gap):
    base_score = 0

    # How often does this prompt fire?
    base_score += gap.frequency_across_runs * 2

    # How many engines show the gap?
    base_score += len(gap.engines_with_gap) * 15

    # How consistently is competitor present?
    base_score += gap.competitor_consistency_rate * 20

    # How high-purchase-intent is this prompt?
    base_score += INTENT_WEIGHTS[gap.prompt_intent] * 10

    if base_score > 70: return "high"
    if base_score > 40: return "medium"
    return "low"
```

## Displacement Event Definition
A displacement event occurs when:
1. In previous run: brand was present in response (brand_present = true)
2. In current run: brand is absent (brand_present = false)
3. AND: a competitor that was not previously present is now present

Displacement events are the highest-priority signals in the system. They are active brand erosion.
