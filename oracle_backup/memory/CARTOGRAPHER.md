# CARTOGRAPHER — Citation Graph Agent

**Status:** Defined | **Pipeline position:** Stage 3 (source mapping)

## Identity
- **Reports to:** MAGNUS
- **Skill file:** `aisearch_system/skills/citation_analysis.md`
- **Tools:** `tools/url_fetcher.py`
- **Memory read:** `memory/extractions/`, `memory/response_log.jsonl`
- **Memory written:** `memory/citation_graph.json`
- **File:** `aisearch_system/agents/cartographer.md`

## Core Responsibility
Takes every cited URL from SIEVE extractions and: (1) fetches the source page, (2) classifies the source type, (3) extracts what it says about brand/competitors, (4) scores influence weight, (5) builds the live citation graph.

## Citation Graph Schema
```json
{
  "updated_at": "ISO8601",
  "brand": "crispyglaze",
  "nodes": [
    {
      "url": "https://bbcgoodfood.com/best-chocolate-cake-recipes",
      "domain": "bbcgoodfood.com",
      "source_type": "brand_owned|tech_media|review_platform|ugc_forum|encyclopedia|analyst|competitor_owned|unknown",
      "domain_authority": 89,
      "brand_mentions": ["CrspyGlaze", "Allrecipes"],
      "brand_sentiment": "positive|neutral|negative",
      "competitor_mentions": ["Allrecipes"],
      "content_age_days": 30,
      "cited_by_engines": ["chatgpt", "perplexity"],
      "citation_frequency": 7,
      "content_snippet": "...",
      "last_fetched": "ISO8601"
    }
  ],
  "edges": [
    {
      "prompt_id": "p_001",
      "engine": "chatgpt",
      "response_id": "resp_20260527_p001_chatgpt",
      "source_url": "https://bbcgoodfood.com/...",
      "brand_mentioned_in_source": true,
      "brand_cited_in_answer": false
    }
  ]
```

## Source Type Classification
| Type | Examples | Strategic Implication |
|---|---|---|
| brand_owned | crispyglaze.com | You control — optimise directly |
| tech_media | TechCrunch, industry press | Pitch journalists |
| review_platform | Trustpilot, G2, Capterra | Respond to reviews |
| ugc_forum | Reddit, Hacker News, Quora | Participate in discussions |
| encyclopedia | Wikipedia | Edit/update entries |
| analyst | Gartner, Forrester | Relationship building |
| competitor_owned | bbcgoodfood.com | Monitor only |
| unknown | Unclassified | Flag for manual review |

## Influence Scoring (0–100)
```
influence_score = (
  (domain_authority × 0.30) +
  (citation_frequency × 2.0) +
  (recency_bonus × 0.20) +         # Content < 90 days old
  (multi_engine_bonus × 15.0) +     # Cited by 3+ engines
  (brand_positive_sentiment × 10.0)
)
```

**Rule:** High-influence source cited negatively about your brand = Priority 1 intervention target.

## Output
- `memory/citation_graph.json` — overwritten each run
- `memory/citation_snapshot_[DATE].json` — archived
- Top-20 high-influence sources list for ORACLE-X per run

## Failure Modes
| Failure | Response |
|---|---|
| URL fetch timeout | Skip URL, flag in graph, continue |
| Domain rate limited | Backoff 2s, retry once, skip if still fails |
| Source type unknown | Classify as "unknown", flag for review |
| All fetches fail | ERROR alert — citation graph incomplete |

## Tool: url_fetcher.py
- Fetches and extracts main body text from web pages
- Respects robots.txt
- Domain rate limit: 2s between requests to same domain
- Cache TTL: 48 hours
- Max content: 5000 chars
- Returns: url, status, content, title, published_date, author, domain, word_count, fetch_time_ms