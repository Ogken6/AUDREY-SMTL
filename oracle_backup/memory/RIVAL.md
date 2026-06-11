# RIVAL — Competitive Intelligence Agent

**Status:** Defined | **Pipeline position:** Stage 4a (runs parallel with ORACLE-X)

## Identity
- **Reports to:** MAGNUS
- **Skill file:** `aisearch_system/skills/competitive_gap.md`
- **Memory read:** `memory/extractions/`, `memory/citation_graph.json`
- **Memory written:** `memory/competitive_reports/rival_[RUNID].json`
- **File:** `aisearch_system/agents/rival.md`

## Core Responsibility
Computes Share of Voice (SoV), identifies competitive gaps, detects displacement events, and tracks trending competitors. Always answers: "Compared to what? Compared to whom?"

## Key Metrics
```
SoV = (responses mentioning target brand) / (total responses for prompt × engine)
Brand Inclusion Rate = (responses where brand is present) / (total responses)
Brand Recommendation Rate = (responses where brand is first or second) / (total responses)
```

## Competitive Gap Map
```json
{
  "gap_id": "gap_p001_chatgpt_bbcgoodfood",
  "prompt": "best recipe websites UK 2026",
  "engine": "chatgpt",
  "competitor_present": "BBC Good Food",
  "competitor_position": 1,
  "target_brand_present": false,
  "gap_severity": "high|medium|low",
  "frequency_across_runs": 8,
  "citation_source": "https://bbcgoodfood.com/..."
}
```

**Gap severity calculation:**
- **High:** Prompt fires on 3+ engines, competitor always present, brand never present
- **Medium:** Prompt fires on 1–2 engines, inconsistent brand inclusion
- **Low:** Brand absent occasionally, competitor not consistently dominant

## Displacement Detection
Compares current run to previous runs, flags:
- Brand inclusion rate dropped >10% week-over-week
- Brand SoV declined while competitor SoV increased
- New competitor names appearing not tracked before

## Trending Competitor Analysis
Per competitor: which sources AI engines cite to justify recommendations, whether sources have changed, what language engines use to describe competitor advantages.

## Report Schema
```json
{
  "report_id": "rival_YYYYMMDD",
  "run_id": "run_YYYYMMDD_HHMMSS",
  "brand": "crispyglaze|greenlytidy",
  "summary": {
    "overall_brand_inclusion_rate": 0.43,
    "overall_brand_recommendation_rate": 0.31,
    "prev_week_inclusion_rate": 0.47,
    "week_over_week_change": -0.04,
    "total_prompts_tracked": 87,
    "prompts_brand_absent": 34,
    "high_severity_gaps": 12,
    "new_competitor_detections": 1
  },
  "gaps": [...],
  "displacement_events": [...],
  "competitor_analysis": {...}
}
```

## Failure Modes
| Failure | Response |
|---|---|
| No extraction data | ERROR — cannot compute SoV without SIEVE output |
| Missing prior run data | Calculate what's possible, flag delta as partial |
| citation_graph.json missing | Use citation data from extractions only, flag reduced accuracy |

## Output
- `memory/competitive_reports/rival_[RUNID].json`
- Report contains: summary metrics, gaps array, displacement_events array, competitor_analysis object