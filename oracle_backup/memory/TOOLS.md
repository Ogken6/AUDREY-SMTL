# TOOLS.md — ORACLE Tool Registry

> Every capability ORACLE has beyond pure reasoning lives in a tool. This document is the authoritative registry of every tool, what it does, who uses it, and how to use it correctly.

---

## Tool Index

| Tool | Used By | Purpose |
|---|---|---|
| `browser_agent.py` | FALCON | Headless browser queries for non-API engines |
| `api_caller.py` | FALCON, SIEVE, ORACLE-X | Unified interface for all LLM API calls |
| `proxy_manager.py` | FALCON | Rotating proxy and session management |
| `url_fetcher.py` | CARTOGRAPHER | Fetch and extract content from citation URLs |
| `db_writer.py` | All agents | PostgreSQL write interface |
| `scheduler.py` | MAGNUS | Job scheduling and queue management |
| `alerter.py` | SENTINEL, MAGNUS | Slack/email/SMS alert dispatching |

**Location:** All tools live at `aisearch_system/tools/`

---

## `browser_agent.py`

**Purpose:** Headless browser queries against AI engines without APIs — Google AI Overviews, Google AI Mode, Microsoft Copilot.

**Key parameters:**
- `wait_for_selector`: CSS selector for the AI response container. **Check before every run** — Google/Microsoft update page structure frequently.
- `timeout_ms`: 15s for Google, 20s for Copilot.
- `session_profile`: Path to a clean Playwright browser profile directory.

**Selector registry:**
```python
SELECTORS = {
 "google_aio": ".IVvmHb",   # Google AI Overview container
 "google_aim": ".SGE-response",  # Google AI Mode (verify before use)
 "copilot": ".cib-chat-main"     # Copilot response container
}
```

**Result schema:**
```json
{
  "raw_text": "string",
  "cited_urls": ["array"],
  "aio_present": bool,
  "screenshot_b64": "string or null",
  "render_time_ms": int,
  "status": "success|timeout|selector_not_found|error",
  "error": "string or null"
}
```

**Error handling:**
- `selector_not_found`: Log `aio_present: false`, do not retry more than once.
- `timeout`: Increase to 25s and retry once. If still timeout, skip and flag.

---

## `api_caller.py`

**Purpose:** Unified interface for all LLM API calls — OpenAI, Anthropic, Google, Perplexity. Handles auth, retries, rate limiting, response normalisation.

**Query an AI engine (FALCON):**
```python
response = caller.query_engine(
 engine="chatgpt",
 prompt="...",
 system_prompt="You are a helpful assistant. Answer naturally.",
 temperature=0.3,
 max_tokens=1500
)
```

**Internal LLM calls (SIEVE, ORACLE-X):**
```python
extraction = caller.internal_call(
 purpose="extraction",  # Maps to prompts/extraction_prompt.md
 content=raw_response_text,
 output_format="json",
 max_tokens=1000
)
```

**Engine configs:**
| Engine | Provider | Model | API Key Env |
|---|---|---|---|
| chatgpt | openai | gpt-4o | OPENAI_API_KEY |
| perplexity | perplexity | llama-3.1-sonar-large-128k-online | PERPLEXITY_API_KEY |
| gemini | google | gemini-2.0-flash-exp | GOOGLE_AI_API_KEY |
| claude | anthropic | claude-sonnet-4-20250514 | ANTHROPIC_API_KEY |

**Retry policy:**
- 429 (rate limit): Exponential backoff — 10s, 30s, 90s. Alert SENTINEL on 3rd failure.
- 5xx: Retry twice with 5s delay. Skip if still failing.
- Timeout: Retry once. Skip if second attempt also times out.

---

## `proxy_manager.py`

**Purpose:** Rotating residential proxy pool for query neutrality and IP-based rate limit avoidance.

**Usage:**
```python
proxy = proxy_mgr.get_proxy(
 region="us-east",        # "us-east", "eu-west", "apac"
 session_type="rotating",  # New IP per request
 protocol="https"
)

health = proxy_mgr.health_check()
# {"pool_size": 150, "available": 147, "blocked": 3, "avg_latency_ms": 340}
```

**Proxy pool requirements:**
- Minimum pool size: 50 residential IPs per region (150 total)
- Rotate IPs every 10 queries per engine
- Never reuse an IP within same engine session within a 2-hour window
- Alert if available < 30 IPs per region

**Session types:**
- `rotating`: New IP per request → Google (aggressive fingerprinting)
- `sticky`: Same IP for session duration (up to 10 min) → Copilot (session continuity needed)

---

## `url_fetcher.py`

**Purpose:** Fetch and extract main readable content from citation URLs.

**Usage:**
```python
result = fetcher.fetch(
 url="https://bbcgoodfood.com/recipe/...",
 extract_main_content=True,  # Strip nav, footer, ads
 max_chars=5000,
 include_metadata=True
)
```

**Result schema:**
```json
{
  "url": "string",
  "status": "success|blocked|not_found|timeout|error",
  "content": "string — main body text, truncated to max_chars",
  "title": "string",
  "published_date": "ISO8601 or null",
  "author": "string or null",
  "domain": "string",
  "content_type": "article|forum|review|wiki|product_page|unknown",
  "word_count": int,
  "fetch_time_ms": int
}
```

**Rules:**
- Always check `robots.txt` before fetching
- Max 1 request per 2 seconds per domain
- Do not fetch URLs behind login walls → log as `status: blocked`
- Do not follow redirects more than 3 hops
- Cache content for 48 hours — check `citation_graph.json` before fetching
- Never cache content from `status: error` or `status: blocked`

---

## `db_writer.py`

**Purpose:** Unified PostgreSQL write interface. Connection pooling, schema validation, transaction management.

**Usage:**
```python
db.write_run_summary(run_summary_dict)
db.write_extractions(extractions_list)
db.write_competitive_report(report_dict)
db.write_action_plan(plan_dict)
db.upsert_citation_node(node_dict)
```

**Transaction guarantees:**
- All writes within a pipeline stage wrapped in a single transaction
- Any write failure → entire stage transaction rolled back
- MAGNUS notified of transaction failures immediately

**Connection:** `DATABASE_URL` env var → Supabase PostgreSQL

---

## `scheduler.py`

**Purpose:** Job scheduling and queue management for MAGNUS.

**Usage:**
```python
# One-time job
sched.schedule_once(
 job_name="full_pipeline_run",
 agent="magnus",
 run_at="2026-05-28T02:00:00Z",
 params={"brand": "acme_corp"}
)

# Recurring job
sched.schedule_recurring(
 job_name="sentinel_health_check",
 agent="sentinel",
 cron="*/15 * * * *"  # Every 15 minutes
)

status = sched.queue_status()
# {"pending": 3, "running": 1, "failed": 0, "next_run": "..."}
```

**Backend:** Redis (`REDIS_URL` env var)

---

## `alerter.py`

**Purpose:** Alert dispatch via Slack, email, SMS.

**Usage:**
```python
alerter.send(
 severity="ERROR",   # INFO|WARNING|ERROR|CRITICAL
 title="FALCON: Google AIO selector failure",
 body="...",
 agent="falcon",
 run_id="run_20260527_020000",
 recovery_ref="heartbeat/recovery_playbook.md#google-aio"
)
```

**Channel routing:**
| Severity | Channel |
|---|---|
| INFO | Slack daily digest only |
| WARNING | Slack `#oracle-alerts` |
| ERROR | Slack `#oracle-alerts` + email to ops team |
| CRITICAL | Slack `#oracle-alerts` + email + SMS to on-call |