# SKILL: Citation Analysis
**Used by:** CARTOGRAPHER
**Version:** 1.0

---

## Purpose
This skill defines how to fetch, classify, and score citation sources from AI engine responses.

## Fetching Protocol

For every URL extracted by SIEVE:
1. Check if URL is already in `memory/citation_graph.json` and was fetched within 48 hours — if yes, use cached version
2. If not cached: fetch with `tools/url_fetcher.py`
3. Extract main content text (strip nav, footer, ads)
4. Truncate to first 5,000 characters (AI engines typically respond to page openings, not deep content)
5. Run brand mention scan across full page content

## Source Classification Decision Tree

```
Is the domain the target brand's own domain?
  → YES: source_type = "brand_owned"
  → NO: Continue

Is the domain a known review platform (G2, Capterra, Trustpilot, etc.)?
  → YES: source_type = "review_platform"
  → NO: Continue

Is the domain Reddit, Hacker News, Quora, or similar?
  → YES: source_type = "ugc_forum"
  → NO: Continue

Is the domain Wikipedia or a wiki?
  → YES: source_type = "encyclopedia"
  → NO: Continue

Is the domain a known tech/business publication?
  → YES: source_type = "tech_media" or "business_media"
  → NO: Continue

Is the domain a known analyst firm?
  → YES: source_type = "analyst"
  → NO: source_type = "unknown" — flag for manual classification
```

## Influence Score Calibration

Recalibrate influence scores monthly. High-citation sources that haven't been cited in 30 days should have their scores decayed by 10% per additional 30-day period of non-citation.
