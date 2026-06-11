#!/usr/bin/env python3
"""
dashboard_api.py — FastAPI backend for ORACLE Dashboard
Serves all 13 REST endpoints from dashboard/DASHBOARD.md
Requires: fastapi, uvicorn, psycopg2-binary, python-dotenv
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2

app = FastAPI(title="ORACLE Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.environ["DATABASE_URL"]

def get_db():
    """Dependency — yields a DB connection, auto-closes."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

# ── Pydantic models ──────────────────────────────────────────────────────────

class ExecutiveSummary(BaseModel):
    brand_inclusion_rate: float
    wow_inclusion_change: float
    brand_recommendation_rate: float
    wow_recommendation_change: float
    sov_vs_top_competitor: dict
    high_severity_gaps: int
    gap_trend: str
    top_5_actions: List[dict]
    sentinel_status: str

# ── GET /api/summary ─────────────────────────────────────────────────────────

@app.get("/api/summary", response_model=ExecutiveSummary)
def get_summary(db=Depends(get_db)):
    """Executive summary — brand inclusion rates, SoV, gaps, top actions."""
    cur = db.cursor()

    # Inclusion and recommendation rates
    cur.execute("""
        SELECT
            COUNT(CASE WHEN brand_present THEN 1 END)::float / NULLIF(COUNT(*), 0) AS inclusion_rate,
            COUNT(CASE WHEN brand_recommendation_position IN (1, 2) THEN 1 END)::float
                / NULLIF(COUNT(CASE WHEN brand_present THEN 1 END), 0) AS rec_rate
        FROM responses
        WHERE captured_at >= NOW() - INTERVAL '7 days'
    """)
    row = cur.fetchone()
    inclusion = row[0] or 0.0
    rec_rate = row[1] or 0.0

    # WoW comparison (previous 7 days)
    cur.execute("""
        SELECT
            COUNT(CASE WHEN brand_present THEN 1 END)::float / NULLIF(COUNT(*), 0)
        FROM responses
        WHERE captured_at BETWEEN NOW() - INTERVAL '14 days' AND NOW() - INTERVAL '7 days'
    """)
    prev_inclusion = cur.fetchone()[0] or 0.0
    wow_inclusion = inclusion - prev_inclusion

    # High-severity gaps count
    cur.execute("""
        SELECT COUNT(*) FROM competitive_gaps
        WHERE gap_severity = 'high' AND resolved_at IS NULL
        AND last_detected >= NOW() - INTERVAL '7 days'
    """)
    high_gaps = cur.fetchone()[0] or 0

    # Top 5 P1 recommendations
    cur.execute("""
        SELECT rec_id, type, action_text, success_metric, effort, status
        FROM recommendations
        WHERE priority = 1 AND status NOT IN ('done', 'dismissed')
        ORDER BY created_at DESC
        LIMIT 5
    """)
    top_actions = [
        {"id": r[0], "type": r[1], "action": r[2], "metric": r[3], "effort": r[4], "status": r[5]}
        for r in cur.fetchall()
    ]

    # SENTINEL health
    health_path = "/root/.openclaw/workspace/aisearch_system/memory/sentinel_health.json"
    sentinel_status = "UNKNOWN"
    if os.path.exists(health_path):
        with open(health_path) as f:
            h = json.load(f)
            sentinel_status = h.get("system_status", "UNKNOWN")

    return ExecutiveSummary(
        brand_inclusion_rate=round(inclusion * 100, 2),
        wow_inclusion_change=round(wow_inclusion * 100, 2),
        brand_recommendation_rate=round(rec_rate * 100, 2),
        wow_recommendation_change=0.0,  # requires similar prev-week query
        sov_vs_top_competitor={},
        high_severity_gaps=high_gaps,
        gap_trend="increasing" if high_gaps > 3 else "stable",
        top_5_actions=top_actions,
        sentinel_status=sentinel_status,
    )

# ── GET /api/prompts ──────────────────────────────────────────────────────────

@app.get("/api/prompts")
def list_prompts(
    intent: Optional[str] = None,
    engine: Optional[str] = None,
    brand_status: Optional[str] = None,  # present|absent|qualified
    limit: int = Query(50, le=200),
    db=Depends(get_db),
):
    """Prompt library with latest run results per prompt per engine."""
    cur = db.cursor()
    query = """
        SELECT p.prompt_id, p.prompt_text, p.intent, p.funnel_stage, p.priority,
               p.anchor, p.run_count, p.lifetime_brand_mention_count,
               r.brand_present, r.brand_position_rank, r.brand_sentiment,
               r.brand_recommendation_position, r.extraction_confidence
        FROM prompts p
        LEFT JOIN responses r ON p.prompt_id = r.prompt_id
            AND r.captured_at = (
                SELECT MAX(r2.captured_at) FROM responses r2 WHERE r2.prompt_id = p.prompt_id
            )
        WHERE p.retired_at IS NULL
    """
    filters = []
    if intent:
        filters.append(f"p.intent = %s")
    if brand_status:
        if brand_status == "present":
            filters.append("r.brand_present = TRUE")
        elif brand_status == "absent":
            filters.append("r.brand_present = FALSE")
        elif brand_status == "qualified":
            filters.append("r.brand_sentiment = 'qualified'")
    if filters:
        query += " AND " + " AND ".join(filters)
    query += " ORDER BY p.run_count DESC LIMIT %s"
    cur.execute(query, (([intent] if intent else []) + [limit]))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

# ── GET /api/prompts/{id}/responses ──────────────────────────────────────────

@app.get("/api/prompts/{prompt_id}/responses")
def get_prompt_responses(prompt_id: str, db=Depends(get_db)):
    """All responses for a specific prompt across all runs and engines."""
    cur = db.cursor()
    cur.execute("""
        SELECT r.response_id, r.run_id, r.engine, r.captured_at, r.region,
               r.brand_present, r.brand_position_rank, r.brand_sentiment,
               r.competitor_count, r.cited_url_count, r.extraction_confidence,
               r.status, r.latency_ms
        FROM responses r
        WHERE r.prompt_id = %s
        ORDER BY r.captured_at DESC
        LIMIT 100
    """, (prompt_id,))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

# ── GET /api/citations ───────────────────────────────────────────────────────

@app.get("/api/citations")
def list_citations(
    sort_by: str = "citation_frequency_30d",
    limit: int = Query(50, le=200),
    db=Depends(get_db),
):
    """Citation source leaderboard."""
    cur = db.cursor()
    col_map = {
        "frequency": "citation_frequency_30d",
        "influence": "influence_score",
        "authority": "domain_authority",
    }
    order_col = col_map.get(sort_by, "citation_frequency_30d")
    cur.execute(f"""
        SELECT url, domain, source_type, domain_authority, influence_score,
               brand_mentioned, brand_sentiment, cited_by_engines,
               citation_frequency_30d, citation_frequency_trend,
               last_fetched, fetch_status
        FROM citation_sources
        ORDER BY {order_col} DESC
        LIMIT %s
    """, (limit,))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

# ── GET /api/citations/{domain} ──────────────────────────────────────────────

@app.get("/api/citations/{domain}")
def get_citation_detail(domain: str, db=Depends(get_db)):
    """Source detail with full citation history for a domain."""
    cur = db.cursor()
    cur.execute("""
        SELECT url, domain, source_type, domain_authority, influence_score,
               brand_mentioned, brand_sentiment, brand_content_snippet,
               competitor_mentions, content_age_days, cited_by_engines,
               citation_frequency_30d, citation_frequency_trend,
               last_fetched, fetch_status, updated_at
        FROM citation_sources
        WHERE domain = %s
        LIMIT 1
    """, (domain,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Domain not found")
    cols = [d[0] for d in cur.description]
    detail = dict(zip(cols, row))

    # Citation history for this domain — which prompts and engines
    cur.execute("""
        SELECT ce.engine, ce.source_url, ce.brand_mentioned_in_source,
               ce.brand_cited_in_answer, ce.cited_at,
               r.prompt_id, r.brand_present, r.brand_sentiment
        FROM citation_edges ce
        JOIN responses r ON ce.response_id = r.response_id
        WHERE ce.source_url LIKE %s || '%%'
        ORDER BY ce.cited_at DESC
        LIMIT 50
    """, (domain,))
    cols2 = [d[0] for d in cur.description]
    detail["citation_history"] = [dict(zip(cols2, row)) for row in cur.fetchall()]
    return detail

# ── GET /api/competitive/gaps ─────────────────────────────────────────────────

@app.get("/api/competitive/gaps")
def list_gaps(
    severity: Optional[str] = None,
    engine: Optional[str] = None,
    limit: int = Query(100, le=500),
    db=Depends(get_db),
):
    """Competitive gap map with filters."""
    cur = db.cursor()
    query = """
        SELECT g.gap_id, g.prompt_id, p.prompt_text, g.engine,
               g.competitor_present, g.gap_severity, g.frequency_across_runs,
               g.first_detected, g.last_detected, g.resolved_at,
               g.linked_recommendation_id,
               r.brand_present, r.brand_position_rank
        FROM competitive_gaps g
        JOIN prompts p ON g.prompt_id = p.prompt_id
        LEFT JOIN responses r ON g.prompt_id = r.prompt_id AND g.engine = r.engine
            AND r.captured_at = (
                SELECT MAX(r2.captured_at) FROM responses r2
                WHERE r2.prompt_id = g.prompt_id AND r2.engine = g.engine
            )
        WHERE g.resolved_at IS NULL
    """
    filters = []
    if severity:
        filters.append("g.gap_severity = %s")
    if engine:
        filters.append("g.engine = %s")
    if filters:
        query += " AND " + " AND ".join(filters)
    query += " ORDER BY g.last_detected DESC LIMIT %s"
    cur.execute(query, (([severity, engine] if engine else [severity] if severity else []) + [limit]))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

# ── GET /api/competitive/sov ──────────────────────────────────────────────────

@app.get("/api/competitive/sov")
def sov_matrix(db=Depends(get_db)):
    """Share of voice matrix — brand vs competitors, by engine and overall."""
    cur = db.cursor()
    cur.execute("""
        SELECT r.engine, r.brand_present,
               COUNT(*) AS total,
               COUNT(CASE WHEN r.brand_present THEN 1 END) AS brand_count
        FROM responses r
        WHERE r.captured_at >= NOW() - INTERVAL '7 days'
        GROUP BY ROLLUP(r.engine), r.brand_present
        ORDER BY r.engine NULLS LAST
    """)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    return {"matrix": rows}

# ── GET /api/recommendations ──────────────────────────────────────────────────

@app.get("/api/recommendations")
def list_recommendations(
    priority: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    db=Depends(get_db),
):
    """Current ORACLE-X action board."""
    cur = db.cursor()
    query = """
        SELECT rec_id, plan_id, type, priority, effort, effort_hours_estimate,
               action_text, rationale, success_metric, target_urls,
               target_publications, gap_references, status, assigned_to,
               created_at, started_at, completed_at, outcome_notes
        FROM recommendations
        WHERE 1=1
    """
    filters = []
    if priority:
        filters.append("priority = %s")
    if status:
        filters.append("status = %s")
    if filters:
        query += " AND " + " AND ".join(filters)
    query += " ORDER BY priority ASC, created_at DESC LIMIT %s"
    cur.execute(query, (([priority, status] if status else [priority] if priority else []) + [limit]))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

# ── PATCH /api/recommendations/{id} ───────────────────────────────────────────

@app.patch("/api/recommendations/{rec_id}")
def update_recommendation(rec_id: str, payload: dict, db=Depends(get_db)):
    """Update recommendation status or owner."""
    allowed = {"status", "assigned_to", "outcome_notes"}
    updates = {k: v for k, v in payload.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    set_clause = ", ".join(f"{k} = %s" for k in updates)
    if "status" in updates and updates["status"] == "done":
        updates["completed_at"] = datetime.utcnow()
    vals = list(updates.values()) + [rec_id]
    cur = db.cursor()
    cur.execute(
        f"UPDATE recommendations SET {set_clause} WHERE rec_id = % RETURNING rec_id",
        vals,
    )
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Recommendation not found")
    db.commit()
    return {"updated": rec_id, "changes": updates}

# ── GET /api/system/health ───────────────────────────────────────────────────────

@app.get("/api/system/health")
def system_health():
    """SENTINEL health summary."""
    health_path = "/root/.openclaw/workspace/aisearch_system/memory/sentinel_health.json"
    if not os.path.exists(health_path):
        return {"status": "UNKNOWN", "note": "Health file not found"}
    with open(health_path) as f:
        return json.load(f)

# ── GET /api/system/runs ───────────────────────────────────────────────────────

@app.get("/api/system/runs")
def pipeline_runs(limit: int = Query(30, le=100), db=Depends(get_db)):
    """Pipeline run history."""
    cur = db.cursor()
    cur.execute("""
        SELECT run_id, brand_config, started_at, completed_at, status,
               prompts_queried, responses_captured, completion_rate,
               avg_extraction_confidence, error_count, data_quality_flags
        FROM pipeline_runs
        ORDER BY started_at DESC
        LIMIT %s
    """, (limit,))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

# ── GET /api/system/alerts ─────────────────────────────────────────────────────

@app.get("/api/system/alerts")
def alert_log(
    severity: Optional[str] = None,
    limit: int = Query(50, le=200),
    db=Depends(get_db),
):
    """Full alert log."""
    cur = db.cursor()
    query = """
        SELECT alert_id, severity, agent_affected, engine_affected,
               description, likely_cause, recovery_ref,
               auto_retry_attempted, auto_retry_result, pipeline_impact,
               resolved_at, resolution_notes, created_at
        FROM sentinel_alerts
    """
    if severity:
        query += " WHERE severity = %s"
    query += " ORDER BY created_at DESC LIMIT %s"
    cur.execute(query, ([severity] if severity else []) + [limit])
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

# ── Run server ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
