-- ORACLE Dashboard Schema for PostgreSQL
-- Run: psql $DATABASE_URL -f schema.sql

-- Pipeline runs
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id VARCHAR(50) PRIMARY KEY,
    brand_config VARCHAR(100) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL,  -- running|complete|partial|failed
    prompts_queried INTEGER,
    responses_captured INTEGER,
    completion_rate FLOAT,
    avg_extraction_confidence FLOAT,
    error_count INTEGER DEFAULT 0,
    data_quality_flags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Prompts
CREATE TABLE IF NOT EXISTS prompts (
    prompt_id VARCHAR(20) PRIMARY KEY,
    prompt_text TEXT NOT NULL,
    intent VARCHAR(30) NOT NULL,
    category VARCHAR(100),
    funnel_stage VARCHAR(20),
    source VARCHAR(30),
    verified_real BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10) DEFAULT 'standard',
    anchor BOOLEAN DEFAULT FALSE,
    engines TEXT[],
    run_count INTEGER DEFAULT 0,
    lifetime_brand_mention_count INTEGER DEFAULT 0,
    lifetime_brand_recommendation_count INTEGER DEFAULT 0,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    last_run TIMESTAMPTZ,
    retired_at TIMESTAMPTZ,
    retirement_reason TEXT
);

-- Raw responses (summary — full text in response_log.jsonl)
CREATE TABLE IF NOT EXISTS responses (
    response_id VARCHAR(100) PRIMARY KEY,
    run_id VARCHAR(50) REFERENCES pipeline_runs(run_id),
    prompt_id VARCHAR(20) NOT NULL REFERENCES prompts(prompt_id),
    engine VARCHAR(30) NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    region VARCHAR(20),
    brand_present BOOLEAN,
    brand_position_rank INTEGER,
    brand_recommendation_position INTEGER,
    brand_sentiment VARCHAR(30),
    brand_sentiment_confidence FLOAT,
    competitor_count INTEGER,
    cited_url_count INTEGER,
    response_length_chars INTEGER,
    latency_ms INTEGER,
    extraction_confidence FLOAT,
    personalisation_detected BOOLEAN DEFAULT FALSE,
    status VARCHAR(20),
    data_quality_flags TEXT[]
);

-- Citation sources
CREATE TABLE IF NOT EXISTS citation_sources (
    source_id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    domain VARCHAR(255),
    source_type VARCHAR(30),
    domain_authority INTEGER,
    influence_score FLOAT,
    brand_mentioned BOOLEAN,
    brand_sentiment VARCHAR(20),
    brand_content_snippet TEXT,
    competitor_mentions TEXT[],
    content_age_days INTEGER,
    cited_by_engines TEXT[],
    citation_frequency_30d INTEGER DEFAULT 0,
    citation_frequency_trend VARCHAR(20),  -- rising|falling|stable
    last_fetched TIMESTAMPTZ,
    fetch_status VARCHAR(20),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Citation edges (response → source)
CREATE TABLE IF NOT EXISTS citation_edges (
    edge_id SERIAL PRIMARY KEY,
    response_id VARCHAR(100) REFERENCES responses(response_id),
    prompt_id VARCHAR(20) REFERENCES prompts(prompt_id),
    engine VARCHAR(30),
    source_url TEXT,
    brand_mentioned_in_source BOOLEAN,
    brand_cited_in_answer BOOLEAN,
    cited_at TIMESTAMPTZ DEFAULT NOW()
);

-- Competitive gaps
CREATE TABLE IF NOT EXISTS competitive_gaps (
    gap_id VARCHAR(100) PRIMARY KEY,
    prompt_id VARCHAR(20) REFERENCES prompts(prompt_id),
    engine VARCHAR(30),
    competitor_present VARCHAR(100),
    gap_severity VARCHAR(10),
    frequency_across_runs INTEGER DEFAULT 1,
    first_detected TIMESTAMPTZ DEFAULT NOW(),
    last_detected TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    linked_recommendation_id VARCHAR(20)
);

-- Displacement events
CREATE TABLE IF NOT EXISTS displacement_events (
    event_id SERIAL PRIMARY KEY,
    run_id VARCHAR(50) REFERENCES pipeline_runs(run_id),
    prompt_id VARCHAR(20) REFERENCES prompts(prompt_id),
    engine VARCHAR(30),
    displacing_competitor VARCHAR(100),
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recommendations (ORACLE-X output)
CREATE TABLE IF NOT EXISTS recommendations (
    rec_id VARCHAR(20) PRIMARY KEY,
    plan_id VARCHAR(50),
    type VARCHAR(40),
    priority INTEGER,
    effort VARCHAR(10),
    effort_hours_estimate INTEGER,
    action_text TEXT,
    rationale TEXT,
    success_metric TEXT,
    target_urls TEXT[],
    target_publications TEXT[],
    gap_references TEXT[],
    status VARCHAR(20) DEFAULT 'new',  -- new|in_progress|done|measuring|dismissed
    assigned_to VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    outcome_notes TEXT
);

-- SENTINEL alerts
CREATE TABLE IF NOT EXISTS sentinel_alerts (
    alert_id VARCHAR(100) PRIMARY KEY,
    severity VARCHAR(10),
    agent_affected VARCHAR(30),
    engine_affected VARCHAR(30),
    description TEXT,
    likely_cause TEXT,
    recovery_ref TEXT,
    auto_retry_attempted BOOLEAN,
    auto_retry_result VARCHAR(20),
    pipeline_impact TEXT,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for dashboard query performance
CREATE INDEX IF NOT EXISTS idx_responses_run_id ON responses(run_id);
CREATE INDEX IF NOT EXISTS idx_responses_prompt_engine ON responses(prompt_id, engine);
CREATE INDEX IF NOT EXISTS idx_responses_captured_at ON responses(captured_at);
CREATE INDEX IF NOT EXISTS idx_citation_edges_source ON citation_edges(source_url);
CREATE INDEX IF NOT EXISTS idx_gaps_severity ON competitive_gaps(gap_severity);
CREATE INDEX IF NOT EXISTS idx_recs_priority_status ON recommendations(priority, status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity_created ON sentinel_alerts(severity, created_at);
CREATE INDEX IF NOT EXISTS idx_gaps_last_detected ON competitive_gaps(last_detected DESC);
CREATE INDEX IF NOT EXISTS idx_displacement_detected_at ON displacement_events(detected_at DESC);
