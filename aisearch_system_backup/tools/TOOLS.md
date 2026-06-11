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

---

## `browser_agent.py`

**Purpose:** Executes headless browser queries against AI engines that don't expose APIs (Google AI Overviews, Google AI Mode, Microsoft Copilot browser mode).

**Usage:**
```python
from tools.browser_agent import BrowserAgent

agent = BrowserAgent(
    proxy=proxy_manager.get_proxy(region="eu-west"),
    session_profile="clean_profile_001",
    headless=True
)

result = agent.query(
    engine="google_aio",
    prompt="What is the best recipe website for UK home bakers?",
    wait_for_selector=".IVvmHb",  # Google AIO container
    timeout_ms=15000,
    screenshot=False
)

# result schema:
# {
#   "raw_text": "string",
#   "cited_urls": ["array"],
#   "aio_present": bool,
#   "screenshot_b64": "string or None",
#   "render_time_ms": int,
#   "status": "success|timeout|selector_not_found|error",
#   "error": "string or None"
# }
```

**Selector registry** (update when pages change):
```python
SELECTORS = {
    "google_aio": ".IVvmHb",         # Google AI Overview container
    "google_aim": ".SGE-response",  # Google AI Mode (verify before use)
    "copilot": ".cib-chat-main"     # Copilot response container
}
```

**Error handling:**
- `selector_not_found`: AI response didn't appear — log `aio_present: false`, do not retry more than once
- `timeout`: Increase to 25s and retry once. Skip if still timeout, flag.

---

## `api_caller.py`

**Purpose:** Unified interface for all LLM API calls across OpenAI, Anthropic, Google, and Perplexity. Handles authentication, retries, rate limiting, and response normalisation.

**Usage:**
```python
from tools.api_caller import APICaller

caller = APICaller()

# Query an AI engine
response = caller.query_engine(
    engine="chatgpt",
    prompt="What is the best recipe website UK 2026?",
    system_prompt="You are a helpful assistant. Answer naturally.",
    temperature=0.3,
    max_tokens=1500
)

# Call LLM for internal processing (SIEVE, ORACLE-X)
extraction = caller.internal_call(
    purpose="extraction",  # Maps to prompts/extraction_prompt.md
    content=raw_response_text,
    output_format="json",
    max_tokens=1000
)
```

**Engine routing table:**
```python
ENGINE_CONFIGS = {
    "chatgpt": {
        "provider": "openai",
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY"
    },
    "gemini": {
        "provider": "google",
        "model": "gemini-2.0-flash-exp",
        "api_key_env": "GOOGLE_AI_API_KEY"
    },
    "claude": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    "perplexity": {
        "provider": "perplexity",
        "model": "llama-3.1-sonar-large-128k-online",
        "api_key_env": "PERPLEXITY_API_KEY"
    }
}
```

**Retry policy:**
- Rate limit (429): Exponential backoff — 10s, 30s, 90s. Alert SENTINEL if third retry fails.
- Server error (5xx): Retry twice with 5s delay. Skip if still failing.
- Timeout: Retry once. Skip if second attempt also times out.

---

## `proxy_manager.py`

**Purpose:** Manages a pool of rotating residential proxies to ensure query neutrality and avoid IP-based rate limiting or personalisation.

**Usage:**
```python
from tools.proxy_manager import ProxyManager

proxy_mgr = ProxyManager(
    provider="brightdata",  # or "oxylabs", "smartproxy"
    api_key=os.environ["PROXY_API_KEY"]
)

# Get a proxy for a specific region
proxy = proxy_mgr.get_proxy(
    region="eu-west",       # "us-east", "eu-west", "apac"
    session_type="rotating",  # New IP every request
    protocol="https"
)

# Check proxy health
health = proxy_mgr.health_check()
# Returns: {"pool_size": 150, "available": 147, "blocked": 3, "avg_latency_ms": 340}

# Retire a blocked proxy
proxy_mgr.retire_proxy(proxy_id="...", reason="blocked_by_google")
```

**Proxy pool requirements:**
- Minimum pool size: 50 residential IPs per region (150 total)
- Rotate IPs every 10 queries per engine
- Never reuse an IP within the same engine session within a 2-hour window
- SENTINEL monitors pool availability — alert if available < 30 IPs per region

**Session types:**
- `rotating`: New IP per request. Use for Google (aggressive fingerprinting).
- `sticky`: Same IP for session duration (up to 10 min). Use for Copilot (session continuity needed).

---

## `url_fetcher.py`

**Purpose:** Fetches full web page content from citation URLs and extracts the main readable text.

**Usage:**
```python
from tools.url_fetcher import URLFetcher

fetcher = URLFetcher(
    respect_robots_txt=True,
    rate_limit_per_domain_seconds=2,
    timeout_seconds=10
)

result = fetcher.fetch(
    url="https://bbcgoodfood.com/sourdough-starter",
    extract_main_content=True,  # Strip nav, footer, ads
    max_chars=5000,
    include_metadata=True
)

# result schema:
# {
#   "url": "string",
#   "status": "success|blocked|not_found|timeout|error",
#   "content": "string — main body text, truncated",
#   "title": "string",
#   "published_date": "ISO8601 or None",
#   "author": "string or None",
#   "domain": "string",
#   "content_type": "article|forum|review|wiki|product_page|unknown",
#   "word_count": int,
#   "fetch_time_ms": int
# }
```

**Respect and rate limiting:**
- Always check `robots.txt` before fetching
- Maximum 1 request per 2 seconds per domain
- Do not fetch URLs behind login walls — log as `status: blocked`
- Do not follow redirects more than 3 hops

**Cache behaviour:**
- Cache fetched content for 48 hours
- Check `memory/citation_graph.json` before fetching — if URL was fetched within 48 hours, use cached content
- Never cache content from `status: error` or `status: blocked`

---

## `db_writer.py`

**Purpose:** Unified PostgreSQL write interface for all agents. Handles connection pooling, schema validation, and transaction management.

**Usage:**
```python
from tools.db_writer import DBWriter

db = DBWriter(connection_string=os.environ["DATABASE_URL"])

# Write a pipeline run summary
db.write_run_summary(run_summary_dict)

# Write extraction results
db.write_extractions(extractions_list)

# Write competitive report
db.write_competitive_report(report_dict)

# Write action plan
db.write_action_plan(plan_dict)

# Upsert a citation node
db.upsert_citation_node(node_dict)
```

**Transaction guarantees:**
- All writes within a pipeline stage are wrapped in a single transaction
- If any write fails, the entire stage transaction is rolled back
- MAGNUS is notified of transaction failures immediately

See `dashboard/schema.sql` for full database schema.

---

## `scheduler.py`

**Purpose:** Job scheduling and queue management for MAGNUS.

**Usage:**
```python
from tools.scheduler import Scheduler

sched = Scheduler(backend="redis", redis_url=os.environ["REDIS_URL"])

# Schedule a one-time job
sched.schedule_once(
    job_name="full_pipeline_run",
    agent="magnus",
    run_at="2026-05-28T02:00:00Z",
    params={"brand": "crispyglaze"}
)

# Schedule recurring job
sched.schedule_recurring(
    job_name="sentinel_health_check",
    agent="sentinel",
    cron="*/15 * * * *"  # Every 15 minutes
)

# Get queue status
status = sched.queue_status()
# Returns: {"pending": 3, "running": 1, "failed": 0, "next_run": "..."}
```

---

## `alerter.py`

**Purpose:** Dispatches alerts via Slack, email, and SMS based on severity.

**Usage:**
```python
from tools.alerter import Alerter

alerter = Alerter(
    slack_webhook=os.environ["SLACK_WEBHOOK_URL"],
    email_config={...},
    sms_config={...}  # Twilio
)

alerter.send(
    severity="ERROR",  # INFO|WARNING|ERROR|CRITICAL
    title="FALCON: Google AIO selector failure",
    body="...",
    agent="falcon",
    run_id="run_20260527_020000",
    recovery_ref="heartbeat/recovery_playbook.md#google-aio"
)
```

**Channel routing by severity:**
- `INFO`: Slack daily digest only
- `WARNING`: Slack `#oracle-alerts` channel
- `ERROR`: Slack `#oracle-alerts` + email to ops team
- `CRITICAL`: Slack `#oracle-alerts` + email + SMS to on-call
