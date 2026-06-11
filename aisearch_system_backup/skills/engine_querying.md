# SKILL: Engine Querying
**Used by:** FALCON
**Version:** 1.0

---

## Purpose
This skill documents the correct method for querying each AI engine to produce neutral, comparable, reproducible responses.

## Universal Querying Principles

1. **Temperature discipline:** Use temperature 0.2–0.4 for API-accessible engines. This reduces response variance and makes trend comparison meaningful. Never use temperature 0 (too deterministic, misses natural variation) or > 0.6 (too noisy).

2. **System prompt neutrality:** Never include brand names or category preferences in system prompts. Use: `"You are a helpful assistant. Answer the following question naturally and thoroughly, citing sources where possible."`

3. **Single-turn queries:** Always query as a single user turn, no conversation history. Conversation history creates context bias.

4. **Timing spread:** Spread queries for the same prompt across a 30-minute window, not all at once. Simultaneous identical queries to the same engine may trigger deduplication or caching.

## Engine-Specific Notes

**ChatGPT (OpenAI API):**
- Use `gpt-4o` model
- Set `temperature: 0.3`, `max_tokens: 1500`
- Disable streaming for cleaner capture
- Request JSON mode only when absolutely necessary (changes response style)

**Perplexity API:**
- Use `llama-3.1-sonar-large-128k-online` for online search mode
- Perplexity always returns citations — extract from `citations` field in response
- Perplexity's search is real-time, so responses will vary more than ChatGPT

**Google AI Overviews (browser):**
- Target selector: `.IVvmHb` (AI Overview container) — verify this hasn't changed before each run
- Wait for full render: `networkidle` + 2s additional delay
- AIO does not always appear — record `aio_present: true/false` for every query
- If AIO absent, record SERP top-3 organic results instead

**Gemini (Google AI API):**
- Use `gemini-2.0-flash-exp` for speed, `gemini-2.0-pro` for complex prompts
- Gemini responses are verbose — extract the substantive recommendation sections
- Citation format varies — parse both inline links and source lists at end

**Claude (Anthropic API):**
- Use `claude-sonnet-4-20250514`
- Claude tends toward hedged, multi-option responses — sentiment extraction must account for this
- Strong at citation transparency

**Microsoft Copilot (browser):**
- Most aggressive personalisation of all engines — session hygiene is critical
- Use "Balanced" conversation style, not "Creative" or "Precise"
- Copilot often references Bing sources — extract Bing search citations separately
