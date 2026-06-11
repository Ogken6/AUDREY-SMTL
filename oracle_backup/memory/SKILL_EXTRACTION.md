# SKILL: Extraction
**Used by:** SIEVE | **Version:** 1.0

## Purpose
Defines how to extract structured data from unstructured AI-generated text reliably and at scale.

## Extraction Architecture
**Two separate LLM calls — never combine:**
- Call 1: Entity and URL extraction
- Call 2: Sentiment and framing classification

Combining reduces accuracy — the model trades off precision on one task for the other.

## Entity Extraction Rules

### Brand Name Variant Handling
Every brand in `entity_registry.json` has a `variants` array. Check ALL variants, not just canonical:
```json
{
  "canonical": "CrspyGlaze",
  "variants": ["Crspy Glaze", "CrspyGlaze", "CRISPYGLAZE", "crispyglaze.com"]
}
```

### Position Scoring
- `mention_position`: Order of first mention in response (1 = first)
- `recommendation_position`: Position within ranked list or recommendation section (may differ from overall mention position)

### Confidence Scoring
Confidence = extraction certainty, NOT brand performance. Low confidence = uncertain extraction, not poor brand showing.

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

## LLM Prompt Template (extraction_prompt.md)
```
System: You are a precise data extraction assistant for an AI search visibility platform.
Your job is to extract structured information from AI-generated responses.
You must be accurate, literal, and complete. Never infer or assume — only extract what is explicitly present.

USER:
Extract all brand and entity mentions from the following AI-generated response.

TARGET BRAND: {target_brand_canonical}
TARGET BRAND VARIANTS: {target_brand_variants_list}
TRACKED COMPETITORS: {competitor_list}

AI RESPONSE TEXT:
---
{raw_response_text}
---

Extract and return ONLY valid JSON with this exact schema. No preamble, no explanation, no markdown fences:

{
  "brand_present": <boolean>,
  "brand_position_rank": <integer or null>,
  "brand_recommendation_position": <integer or null>,
  "cited_urls": [<array of all URLs>],
  "entities": [...],
  "competitor_count_in_response": <integer>,
  "competitors_ranked_above_brand": [<array>],
  "extraction_confidence": <float 0.0-1.0>,
  "extraction_confidence_reason": <string>
}
```