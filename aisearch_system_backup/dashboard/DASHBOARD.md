# DASHBOARD.md — ORACLE Dashboard Design & Data Model

---

## Overview

The ORACLE dashboard is a React frontend backed by a FastAPI Python API, querying a PostgreSQL database. It gives human operators and stakeholders a live view of brand AI visibility, competitive position, citation health, and pending actions.

It is designed around one principle: **every number on the dashboard traces back to a specific prompt, a specific engine response, and a specific source**. Nothing is anonymous aggregation.

---

## Dashboard Views

### View 1: Executive Summary (default home)

**Audience:** Marketing leads, CMOs, brand managers
**Update frequency:** After each pipeline run (daily)

Displays:
- **Brand AI Inclusion Rate** — % of tracked prompts where brand appears, across all engines. With week-over-week sparkline.
- **Brand Recommendation Rate** — % of prompts where brand is first or second recommendation.
- **Share of Voice vs. Top Competitor** — Side-by-side comparison.
- **Active High-Severity Gaps** — Count with trend (increasing/decreasing).
- **Top 5 P1 Actions** — ORACLE-X recommendations, with status tracking.
- **System Health Badge** — SENTINEL's current status (green/amber/red).

---

### View 2: Prompt Explorer

**Audience:** SEO/content teams
**Update frequency:** Real-time (latest run data)

For each prompt in the library:
- Prompt text and intent classification
- Engine-by-engine inclusion table (✅ brand present / ❌ absent / ⚠️ qualified)
- Historical trend (14-day sparkline per engine)
- Which competitors appear in each response
- Cited sources for each response
- Click through to see the full raw response

Filters: by intent, by engine, by funnel stage, by brand inclusion status, by gap severity

---

### View 3: Citation Intelligence

**Audience:** Content and PR teams
**Update frequency:** Every 6 hours (CARTOGRAPHER update)

- **Citation Map:** Visual graph of the top 30 most-cited sources, sized by influence score
- **Source Leaderboard:** Table of all tracked sources, sortable by citation frequency, domain authority, brand sentiment, engine coverage
- **Intervention Tracker:** Sources flagged as high-influence + brand-negative, with linked ORACLE-X recommendation and status
- **Source Detail Panel:** Click any source to see: full content excerpt, which prompts trigger its citation, which engines cite it, brand sentiment analysis

---

### View 4: Competitive Analysis

**Audience:** Strategy and marketing teams
**Update frequency:** Daily (after RIVAL runs)

- **Share of Voice Matrix:** Heatmap of brand SoV vs. each competitor, by engine and prompt cluster
- **Displacement Timeline:** Chronological log of displacement events with severity
- **Competitor Citation Sources:** Which sources are being used to justify competitor recommendations
- **Gap Map:** Full list of competitive gaps, filterable by severity, engine, intent type
- **Emerging Competitor Alerts:** Newly detected competitors with appearance frequency

---

### View 5: ORACLE-X Action Board

**Audience:** All stakeholders
**Update frequency:** Weekly (after ORACLE-X runs)

- **Kanban board:** P1/P2/P3/P4 recommendation cards with status (New → In Progress → Done → Measuring)
- Each card shows: recommendation type, specific action, rationale, success metric, effort estimate, assigned owner
- **Impact Tracking:** For completed recommendations, before/after metrics comparison
- **Recommendation History:** Archive of all past recommendations with outcome data

---

### View 6: System Operations (SENTINEL View)

**Audience:** Technical operators
**Update frequency:** Every 15 minutes

- **Agent Status Board:** Liveness status for each named agent
- **Pipeline Run History:** Last 30 runs with completion rates, errors, stage durations
- **API Health:** Status of each external API with latency and error rate
- **Proxy Pool Status:** Available IPs per region
- **Disk & DB Metrics:** Storage consumption, backup status
- **Alert Log:** Full chronological alert history with resolution status

---

## Tech Stack

- **Frontend:** React (single-page app)
- **Backend:** FastAPI Python
- **Database:** PostgreSQL
- **Charts:** Chart.js or Recharts (CDN)
- **Real-time:** Polling every 5 minutes or SSE for critical alerts

---

## API Endpoints (FastAPI)

```
GET  /api/summary                    → Executive summary metrics
GET  /api/prompts                    → Prompt library with latest run results
GET  /api/prompts/{id}/responses     → All responses for a specific prompt
GET  /api/citations                  → Citation source leaderboard
GET  /api/citations/{domain}         → Source detail with full citation history
GET  /api/competitive/gaps          → Gap map with filters
GET  /api/competitive/sov            → Share of voice matrix
GET  /api/recommendations            → Current action board
PATCH /api/recommendations/{id}      → Update recommendation status/owner
GET  /api/system/health              → SENTINEL health summary
GET  /api/system/runs                → Pipeline run history
GET  /api/system/alerts              → Alert log
```

---

## Data Retention & Access Control

- **Prompts:** Never deleted — append-only; retired prompts preserved with `retired_at` timestamp
- **Responses:** Summary records in PostgreSQL; full raw text in `response_log.jsonl`
- **Citation sources:** Updated in-place per run; historical influence shown via `citation_frequency_30d` trend
- **Recommendations:** All states preserved; completed ones retain outcome data for impact tracking
- **Alerts:** Append-only log; resolved alerts retain resolution notes
