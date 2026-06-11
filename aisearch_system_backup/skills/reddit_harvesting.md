# Skill: Reddit Harvesting

How SCOUT scrapes Reddit to extract real user questions as verified prompts.

## Reddit Harvesting Protocol

### Target Subreddits
Target 5 relevant subreddits per brand category. For crispyglaze (recipe/baking):
- r/Baking, r/Breadit, r/EatAndPunch, r/recipes, r/Cooking

For greenlytidy (sustainable living):
- r/sustainability, r/ZeroWaste, r/Frugal, r/EthicalLiving, r/SimpleLiving

### Query Parameters
- Sort: `top` (upvotes = genuine intent signal)
- Time filter: `month` (recent active discussions)
- Minimum upvotes: 10 (filters test posts from genuine ones)
- Post type: `text` only (links and images don't contain question text)

### Extraction Process
```
1. GET /r/[subreddit]/top.json?t=month&limit=100
2. Filter posts with score >= 10
3. For each post:
   - Extract title (primary intent signal)
   - Extract selftext if available (deeper intent context)
   - Normalise: fix punctuation, trim, lowercase for dedup
   - Classify intent type from title keywords
4. Add to candidate pool as {text, source: "reddit", verified_real: true}
5. Deduplicate against existing library (exact match first, then semantic)
```

### Deduplication Rules
- Exact match: same lowercase string → skip
- Semantic match: cosine similarity > 0.92 against any library prompt → skip
- First-seen date: record `added_at` for every new prompt

### Failure Modes
| Failure | Response |
|---|---|
| HTTP 429 (rate limit) | Wait 60s, retry once. If fails again, skip subreddit for this run |
| Subreddit not found | Remove from target list, alert MAGNUS |
| JSON parse failure | Skip post, log error, continue |
| All subreddits rate limited | Use last cached harvest; alert MAGNUS degraded |

### Tool Use
```python
# Example using requests
import requests

def harvest_reddit(subreddit, min_upvotes=10):
    headers = {"User-Agent": "ORACLE-SCOUT/1.0 (prompt intelligence)"}
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t=month&limit=100"
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code == 200:
        posts = resp.json()["data"]["children"]
        return [p["data"] for p in posts if p["data"]["score"] >= min_upvotes]
    elif resp.status_code == 429:
        raise RateLimitError("Reddit rate limited")
    else:
        raise Exception(f"Reddit returned {resp.status_code}")
```
