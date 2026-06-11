# SIEVE — Parsing & Extraction Agent

**Status:** Defined | **Pipeline position:** Stage 2 (structuring raw responses)

## Identity
- **Reports to:** MAGNUS
- **Skill files:** `aisearch_system/skills/extraction.md`, `aisearch_system/skills/sentiment_framing.md`
- **Tools:** `tools/api_caller.py`
- **Memory read:** `memory/response_log.jsonl` (raw responses from FALCON), `memory/entity_registry.json`
- **Memory written:** `memory/extractions/run_[RUNID]_sieve.jsonl`
- **File:** `aisearch_system/agents/sieve.md`

## Core Responsibility
Takes raw AI responses from FALCON and extracts structured data via LLM-based parsing. Two-stage pipeline: Entity Extraction → Sentiment Framing. Never modifies raw response data.

## Stage 1: Entity Extraction
LLM call with `prompts/extraction_prompt.md`. Extracts:
- All brand mentions (target brand + competitors)
- Mention position, context, whether recommended, whether cited
- All cited URLs
- Brand presence flag, position rank, competitor count
- Extraction confidence score (0–1)

## Stage 2: Sentiment Framing
Separate LLM call with `prompts/sentiment_prompt.md`. Classifies each brand mention:

| Class | Definition |
|---|---|
| strong_recommend | Explicitly recommended as best choice |
| recommend | Mentioned positively as valid option |
| neutral | Mentioned without positive or negative framing |
| qualified | Recommended with significant caveats |
| negative | Mentioned with negative framing |
| absent | Not mentioned at all |

Confidence below 0.70 → flagged for human review.

## Extraction Output Schema
```json
{
  "response_id": "resp_20260527_p001_chatgpt",
  "extracted_at": "ISO8601",
  "entities": [
    {
      "name": "CrspyGlaze",
      "type": "brand",
      "is_target_brand": true,
      "mention_position": 1,
      "mention_context": "first recommendation",
      "is_recommended": true,
      "is_cited": false,
      "qualifier": null,
      "sentiment": "strong_recommend",
      "sentiment_confidence": 0.94
    }
  ],
  "cited_urls": ["https://bbcgoodfood.com/...", "https://reddit.com/r/baking/..."],
  "brand_present": true,
  "brand_position_rank": 1,
  "competitor_count": 2,
  "extraction_confidence": 0.92
}
```

## Quality Rules
1. Never modify raw response — extraction only
2. Every extraction must have confidence score
3. Confidence < 0.65 → flag for human review, do not pass to CARTOGRAPHER without flag
4. Entity extraction + sentiment = **separate LLM calls** (never combined)
5. Cross-reference against `entity_registry.json` for name variants

## Failure Modes
| Failure | Response |
|---|---|
| Single response parse failure | Skip, flag, continue |
| LLM extraction timeout | Flag low-confidence, include raw text reference |
| All extractions fail | ERROR alert to MAGNUS |
| entity_registry.json missing | CRITICAL — SIEVE cannot validate brand variants |

## Output
- One JSONL file per run: `memory/extractions/run_[RUNID]_sieve.jsonl`
- Append-only, one record per response