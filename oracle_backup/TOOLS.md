# TOOLS.md — ORACLE Tool Registry

Full tool registry: `memory/TOOLS.md`

## Tool Index

| Tool | Used By | Purpose |
|---|---|---|
| `browser_agent.py` | FALCON | Headless browser for Google AIO, AI Mode, Copilot |
| `api_caller.py` | FALCON, SIEVE, ORACLE-X | Unified LLM API interface |
| `proxy_manager.py` | FALCON | Rotating residential proxy pool |
| `url_fetcher.py` | CARTOGRAPHER | Citation URL content extraction |
| `db_writer.py` | All agents | PostgreSQL write interface |
| `scheduler.py` | MAGNUS | Job scheduling via Redis |
| `alerter.py` | SENTINEL, MAGNUS | Slack/email/SMS alert dispatch |

**Location:** `aisearch_system/tools/`

## Quick Reference

### browser_agent.py
- Google AIO selector: `.IVvmHb` — **verify before every run**
- Google AI Mode selector: `.SGE-response` — verify before use
- Copilot selector: `.cib-chat-main`
- Timeouts: 15s Google, 20s Copilot, 25s retry

### api_caller.py
- Engines: chatgpt (gpt-4o), perplexity (sonar), gemini (2.0-flash-exp), claude (sonnet-4-20250514)
- Retry on 429: 10s → 30s → 90s backoff; alert SENTINEL on 3rd failure
- Retry on 5xx: 2 retries, 5s delay
- Retry on timeout: 1 retry

### proxy_manager.py
- Pool: min 50 residential IPs per region (150 total)
- Rotate every 10 queries per engine
- Min available: 30 IPs per region — alert below this
- Session types: `rotating` (Google), `sticky` (Copilot, up to 10min)

### url_fetcher.py
- Rate limit: 1 req/2s per domain
- Max chars: 5,000
- Cache TTL: 48 hours
- Check citation_graph.json before fetching

### alerter.py
- WARNING → Slack `#oracle-alerts`
- ERROR → Slack + email
- CRITICAL → Slack + email + SMS

### db_writer.py
- PostgreSQL via Supabase (`DATABASE_URL`)
- All writes in a stage are one transaction — all-or-nothing

### scheduler.py
- Backend: Redis (`REDIS_URL`)
- Cron format: standard 5-field cron expression
- SENTINEL health check: `*/15 * * * *`