# Skill: PAA (People Also Ask) Extraction

How SCOUT harvests "People Also Ask" questions from Google SERPs to build real query intelligence.

## PAA Extraction Protocol

### Seed Query Strategy
Fire 10–15 broad category queries at Google. For each category, pick the most common question root forms:

For recipe/baking (crispyglaze):
- "best baking recipes UK"
- "easy bread recipes at home"
- " chocolate cake from scratch UK"
- "sourdough starter guide"
- "home baking tips 2026"

For sustainable living (greenlytidy):
- "eco-friendly products UK"
- "how to reduce waste at home"
- "sustainable living tips beginners"
- "best zero waste products UK"

### Extraction Process
```
1. Use browser agent or SERP API to collect PAA for each seed query
2. Extract each PAA question (format: <div class="related-question">...</div>)
3. Normalise: fix encoding, trim whitespace
4. Add as {text, SOURCE: "google_paa", verified_real: true}
5. Deduplicate against existing prompt library
```

### Deduplication with Prompt Library
- Check against all existing prompts: same text → skip
- Semantic dedup: embedding cosine similarity > 0.92 → skip
- Accept if net new word count > 5 (prevents near-identical PAA variants from inflating library)

### PAA Result Schema
```json
{
  "query": "best baking recipes UK",
  "paa_questions": [
    "What are Jamie's top baking recipes?",
    "How do I start baking at home for beginners?",
    "What ingredients do I need for basic baking?"
  ],
  "collected_at": "2026-05-27T12:09:00Z",
  "source": "google_paa"
}
```

### Google PAA Notes
- PAA boxes typically show 8–10 questions per query
- Not all PAA questions are unique across queries — dedup is critical
- PAA data is public and scraping Google for this purpose is generally acceptable at low volume

### Failure Modes
| Failure | Response |
|---|---|
| Google rate limited (503) | Wait 30s, retry once |
| No PAA box found | Log: "No PAA for query", continue |
| Browser agent timeout | Log error, skip query |
| All queries fail | Alert MAGNUS: SCOUT PAA harvest degraded |
