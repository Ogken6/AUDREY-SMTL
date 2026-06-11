# SKILL: Engine Querying
**Used by:** FALCON | **Version:** 1.0

## Purpose
Documents correct method for querying each AI engine to produce neutral, comparable, reproducible responses.

## Universal Querying Principles

1. **Temperature discipline:** 0.2–0.4 for API-accessible engines. Never 0 (too deterministic) or >0.6 (too noisy).

2. **System prompt neutrality:** Never include brand names or category preferences. Use:
   `"You are a helpful assistant. Answer the following question naturally and thoroughly, citing sources where possible."`

3. **Single-turn queries:** Always query as a single user turn, no conversation history. History creates context bias.

4. **Timing spread:** Spread queries for the same prompt across a 30-minute window. Simultaneous identical queries may trigger deduplication or caching.

## Per-Engine Notes

| Engine | Method | Key Rules |
|---|---|---|
| **ChatGPT** | OpenAI API, gpt-4o | temp: 0.3, max_tokens: 1500, disable streaming, avoid JSON mode |
| **Perplexity** | Perplexity API, llama-3.1-sonar-large-128k-online | Always returns citations in `citations` field; real-time = more variation |
| **Google AIO** | Browser (Playwright) | Target selector: `.IVvmHb` — verify before each run; wait `networkidle`+2s; record `aio_present: true/false`; if absent record top-3 organic |
| **Gemini** | Google AI API, gemini-2.0-flash-exp | Verbose output — extract substantive recommendation sections; citation format varies |
| **Claude** | Anthropic API, claude-sonnet-4-20250514 | Hedged, multi-option responses — sentiment must account for this; strong citation transparency |
| **Copilot** | Browser | Most aggressive personalisation; use "Balanced" style; extract Bing citations separately |

## Response Capture Requirements
Every response must capture:
- `raw_response`: full unmodified AI text
- `cited_urls`: all URLs in the response
- `latency_ms`: query execution time
- `region`: us-east | eu-west | apac
- `aio_present`: true/false (Google AIO only)
- `personalisation_detected`: flag

## Neutrality Enforcement
- Never reuse browser session across engines
- Never reuse session that returned a branded result
- Rotate proxy IPs every 10 queries per engine
- Randomise query timing within batch (1–5s delay)
- Never query from brand's own IP ranges