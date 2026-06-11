# SKILL: Citation Analysis
**Used by:** CARTOGRAPHER | **Version:** 1.0

## Purpose
Defines how to fetch, classify, and score citation sources from AI engine responses.

## Fetching Protocol
For every URL extracted by SIEVE:
1. Check if URL is in `citation_graph.json` and was fetched within 48 hours → use cached if yes
2. If not cached: fetch with `tools/url_fetcher.py`
3. Extract main content text (strip nav, footer, ads)
4. Truncate to first 5,000 characters (AI engines respond to page openings, not deep content)
5. Run brand mention scan across full page content

## Source Classification Decision Tree
```
Is the domain the target brand's own domain?
  → YES: source_type = "brand_owned"

Is it a known review platform (G2, Capterra, Trustpilot)?
  → YES: source_type = "review_platform"

Is it Reddit, Hacker News, Quora, or similar?
  → YES: source_type = "ugc_forum"

Is it Wikipedia or a wiki?
  → YES: source_type = "encyclopedia"

Is it a known tech/business publication?
  → YES: source_type = "tech_media" or "business_media"

Is it a known analyst firm?
  → YES: source_type = "analyst"

→ NO: source_type = "unknown" — flag for manual classification
```

## Influence Score (0–100)
```
influence_score = (
  (domain_authority × 0.30) +
  (citation_frequency × 2.0) +
  (recency_bonus × 0.20) +          # Content < 90 days old
  (multi_engine_bonus × 15.0) +     # Cited by 3+ engines
  (brand_positive_sentiment × 10.0)
)
```

**Recalibration:** Monthly. Sources not cited in 30 days → decay score by 10% per additional 30-day period of non-citation.

## Source Type Strategic Implication
| Type | Implication |
|---|---|
| brand_owned | You control — optimise directly |
| tech_media | Pitch journalists |
| review_platform | Respond to reviews |
| ugc_forum | Participate in discussions |
| encyclopedia | Edit/update entries |
| analyst | Relationship building |
| competitor_owned | Monitor only |
| unknown | Flag for manual review |

**Rule:** High-influence source cited negatively about your brand = Priority 1 intervention target.