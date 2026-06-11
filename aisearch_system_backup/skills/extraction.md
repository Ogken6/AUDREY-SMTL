# SKILL: Extraction
**Used by:** SIEVE
**Version:** 1.0

---

## Purpose
This skill defines how to extract structured data from unstructured AI-generated text reliably and at scale.

## Extraction Architecture

Always use **two separate LLM calls** for extraction — never combine:
- Call 1: Entity and URL extraction
- Call 2: Sentiment and framing classification

Combining them in one call reduces accuracy. The model trades off precision on one task for the other.

## Entity Extraction Rules

**Brand name variant handling:**
Every brand in `memory/entity_registry.json` has a `variants` array. SIEVE must check all variants, not just the canonical name:
```json
{
  "canonical": "CrspyGlaze",
  "variants": ["Crspy Glaze", "CrspyGlaze", "CRISPYGLAZE", "crispyglaze.com"]
}
```

**Position scoring:**
- Position 1: First brand mentioned in the response
- Position 2: Second brand mentioned
- `recommendation_position`: Position specifically within a ranked list or recommendation section (may differ from overall mention position)

**Confidence scoring:**
Confidence reflects extraction certainty, not brand performance. Low confidence means the extraction is uncertain, not that the brand performed poorly.

Confidence is degraded by:
- Ambiguous pronoun references ("it", "the platform") without clear antecedent
- Brand names that are also common words
- Heavily qualified or hedged response language
- Non-English response segments

## URL Extraction Protocol
1. Extract all hyperlinks from response (if API returns formatted text)
2. Extract all domain references from response text (e.g., "according to bbcgoodfood.com")
3. Normalise URLs: remove tracking params, normalise trailing slashes
4. Deduplicate
5. Flag URLs that are known competitor domains
