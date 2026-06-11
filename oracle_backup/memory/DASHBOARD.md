# DASHBOARD.md — ORACLE Dashboard Design & Data Model

**File:** `aisearch_system/dashboard/DASHBOARD.md`

## Architecture
- **Frontend:** React
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (Supabase)

**Core principle:** Every number on the dashboard traces back to a specific prompt, engine response, and source. Nothing is anonymous aggregation.

---

## 6 Dashboard Views

### View 1: Executive Summary (default home)
**Audience:** Marketing leads, CMOs, brand managers | **Update:** After each pipeline run (daily)

Displays:
- Brand AI Inclusion Rate (% prompts where brand appears, all engines) + WoW sparkline
- Brand Recommendation Rate (% prompts where brand is 1st or 2nd recommendation)
- Share of Voice vs. Top Competitor (side-by-side)
- Active High-Severity Gaps (count + trend)
- Top 5 P1 Actions (ORACLE-X recommendations with status tracking)
- System Health Badge (SENTINEL: green/amber/red)

---

### View 2: Prompt Explorer
**Audience:** SEO/content teams | **Update:** Real-time (latest run data)

Per prompt:
- Prompt text + intent classification
- Engine-by-engine inclusion table (✅ present / ❌ absent / ⚠️ qualified)
- 14-day sparkline per engine
- Competitors appearing in each response
- Cited sources per response
- Full raw response (click-through)

Filters: intent, engine, funnel stage, brand inclusion status, gap severity

---

### View 3: Citation Intelligence
**Audience:** Content and PR teams | **Update:** Every 6 hours (CARTOGRAPHER)

- Citation Map: visual graph of top 30 most-cited sources, sized by influence score
- Source Leaderboard: sortable by citation frequency, domain authority, brand sentiment, engine coverage
- Intervention Tracker: high-influence + brand-negative sources with linked ORACLE-X recommendation
- Source Detail Panel: content excerpt, prompts triggering citation, engines citing it, brand sentiment

---

### View 4: Competitive Analysis
**Audience:** Strategy and marketing teams | **Update:** Daily (after RIVAL)

- Share of Voice Matrix: heatmap brand vs. each competitor, by engine and prompt cluster
- Displacement Timeline: chronological log of displacement events with severity
- Competitor Citation Sources: sources used to justify competitor recommendations
- Gap Map: full gap list, filterable by severity, engine, intent
- Emerging Competitor Alerts: newly detected competitors with appearance frequency

---

### View 5: ORACLE-X Action Board
**Audience:** All stakeholders | **Update:** Weekly (after ORACLE-X)

- Kanban board: P1/P2/P3/P4 cards — New → In Progress → Done → Measuring
- Each card: recommendation type, action, rationale, success metric, effort estimate, owner
- Impact Tracking: before/after metrics for completed recommendations
- Recommendation History: archive of all past recommendations with outcomes

---

### View 6: System Operations (SENTINEL View)
**Audience:** Technical operators | **Update:** Every 15 minutes

- Agent Status Board: liveness for each named agent
- Pipeline Run History: last 30 runs, completion rates, errors, stage durations
- API Health: status of each external API with latency and error rate
- Proxy Pool Status: available IPs per region
- Disk & DB Metrics: storage consumption, backup status
- Alert Log: chronological alert history with resolution status

---

## Database Schema

### Core Tables

**`pipeline_runs`** — one row per pipeline execution
```
run_id, brand_config, started_at, completed_at, status (running/complete/partial/failed),
prompts_queried, responses_captured, completion_rate, avg_extraction_confidence,
error_count, data_quality_flags, created_at
```

**`responses`** — summary row per prompt×engine response (full text in JSONL)
```
response_id, run_id, prompt_id, engine, captured_at, region,
brand_present, brand_position_rank, brand_recommendation_position,
brand_sentiment, brand_sentiment_confidence, competitor_count, cited_url_count,
response_length_chars, latency_ms, extraction_confidence,
personalisation_detected, status, data_quality_flags
```

**`prompts`** — master prompt library
```
prompt_id, prompt_text, intent, category, funnel_stage, source,
verified_real, priority, anchor, engines, run_count,
lifetime_brand_mention_count, lifetime_brand_recommendation_count,
added_at, last_run, retired_at, retirement_reason
```

**`citation_sources`** — one row per unique cited URL
```
source_id, url (unique), domain, source_type, domain_authority,
influence_score, brand_mentioned, brand_sentiment, brand_content_snippet,
competitor_mentions, content_age_days, cited_by_engines,
citation_frequency_30d, citation_frequency_trend, last_fetched, fetch_status
```

**`citation_edges`** — response → source relationship
```
edge_id, response_id, prompt_id, engine, source_url,
brand_mentioned_in_source, brand_cited_in_answer, cited_at
```

**`competitive_gaps`** — identified gaps
```
gap_id, prompt_id, engine, competitor_present, gap_severity,
frequency_across_runs, first_detected, last_detected,
resolved_at, linked_recommendation_id
```

**`displacement_events`** — brand erosion events
```
event_id, run_id, prompt_id, engine, displacing_competitor, detected_at
```

**`recommendations`** — ORACLE-X output + tracking
```
rec_id, plan_id, type, priority, effort, effort_hours_estimate,
action_text, rationale, success_metric, target_urls, target_publications,
gap_references, status (new/in_progress/done/measuring/dismissed),
assigned_to, created_at, started_at, completed_at, outcome_notes
```

**`sentinel_alerts`** — alert history
```
alert_id, severity, agent_affected, engine_affected, description,
likely_cause, recovery_ref, auto_retry_attempted, auto_retry_result,
pipeline_impact, resolved_at, resolution_notes, created_at
```

### Key Indexes
```
idx_responses_run_id              ON responses(run_id)
idx_responses_prompt_engine        ON responses(prompt_id, engine)
idx_responses_captured_at          ON responses(captured_at)
idx_citation_edges_source          ON citation_edges(source_url)
idx_gaps_severity                  ON competitive_gaps(gap_severity)
idx_recs_priority_status           ON recommendations(priority, status)
idx_alerts_severity_created        ON sentinel_alerts(severity, created_at)
```

---

## API Endpoints (FastAPI)

| Method | Endpoint | Returns |
|---|---|---|
| GET | `/api/summary` | Executive summary metrics |
| GET | `/api/prompts` | Prompt library + latest run results |
| GET | `/api/prompts/{id}/responses` | All responses for a specific prompt |
| GET | `/api/citations` | Citation source leaderboard |
| GET | `/api/citations/{domain}` | Source detail + full citation history |
| GET | `/api/competitive/gaps` | Gap map with filters |
| GET | `/api/competitive/sov` | Share of voice matrix |
| GET | `/api/recommendations` | Current action board |
| PATCH | `/api/recommendations/{id}` | Update recommendation status/owner |
| GET | `/api/system/health` | SENTINEL health summary |
| GET | `/api/system/runs` | Pipeline run history |
| GET | `/api/system/alerts` | Alert log |