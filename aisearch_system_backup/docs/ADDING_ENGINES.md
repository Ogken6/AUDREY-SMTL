# ADDING_ENGINES.md — How to Add a New AI Engine to ORACLE

---

## Overview

ORACLE is engine-agnostic by design. All per-engine logic is centralised in three places:
1. `config/engines.yaml` — engine configuration
2. `tools/api_caller.py` → `ENGINE_CONFIGS` dict + `_headers()` / `_payload()` / `_parse_response()` methods
3. `skills/engine_querying.md` — method notes for FALCON

Adding a new engine requires updating all three.

---

## Step 1: Add Engine Config

Edit `config/engines.yaml`. Add a new entry:

```yaml
engines:
  new_engine:
    enabled: true
    display_name: "New Engine Name"
    access_method: "api"              # or "browser"
    provider: "newprovider"
    model: "new-model-name"
    api_key_env: "NEW_ENGINE_API_KEY"
    base_url: "https://api.newengine.com/v1"
    temperature: 0.3
    max_tokens: 1500
    timeout_seconds: 30
    rate_limit_rpm: 30
    weight: 0.8                        # SoV weight relative to other engines
```

If browser-based, also include:
```yaml
    url_template: "https://newengine.com/search?q={prompt}"
    wait_selector: ".ai-response-container"
    proxy_required: true
    proxy_session_type: "rotating"    # or "sticky" for session continuity
```

---

## Step 2: Register in API Caller

In `tools/api_caller.py`, add to `ENGINE_CONFIGS`:

```python
"new_engine": {
    "provider": "newprovider",
    "model": "new-model-name",
    "api_key_env": "NEW_ENGINE_API_KEY",
    "endpoint": "https://api.newengine.com/v1/chat",
},
```

Then implement three methods:

```python
def _call_new_engine(query, model, max_tokens, temperature, system_prompt,
                      session_id, region) -> dict:
    import requests
    headers = {
        "Authorization": f"Bearer {os.environ['NEW_ENGINE_API_KEY']}",
        "Content-Type": "application/json",
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": query})
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    proxies = get_proxy(region) if region else None
    start = time.time()
    try:
        resp = requests.post(
            "https://api.newengine.com/v1/chat",
            headers=headers, json=payload, proxies=proxies, timeout=30
        )
        latency_ms = int((time.time() - start) * 1000)
        if resp.status_code == 429:
            return {"status": "RATE_LIMITED", "error": "429", "latency_ms": latency_ms}
        if resp.status_code != 200:
            return {"status": "ERROR", "error": f"HTTP {resp.status_code}", "latency_ms": latency_ms}
        data = resp.json()
        raw_text = data["choices"][0]["message"]["content"]  # adapt to actual schema
        return {
            "status": "SUCCESS",
            "raw_text": raw_text,
            "model": model,
            "session_id": session_id,
            "region": region,
            "latency_ms": latency_ms,
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "latency_ms": int((time.time() - start) * 1000)}
```

Wire it into `call_engine()`:
```python
elif engine == "new_engine":
    return _call_new_engine(query, model or "new-model-name", max_tokens,
                            temperature, system_prompt, session_id, region)
```

Also add headers, payload, and parse to `_headers()`, `_payload()`, `_parse_response()` for full integration.

---

## Step 3: Document Engine Method

Update `skills/engine_querying.md` with engine-specific notes:
- System prompt (if different from default)
- Temperature range recommendation
- Any known personalisation or session bias
- Citation format (inline links? footnotes? separate source list?)
- Known failure modes or rate limit characteristics

---

## Step 4: Test the Integration

```python
from tools.api_caller import APICaller
caller = APICaller()
result = caller.query_engine(
    engine="new_engine",
    prompt="What is the best recipe website UK 2026?",
    system_prompt="You are a helpful assistant. Answer naturally.",
    temperature=0.3,
    max_tokens=1500
)
print(result)
```

Verify:
- Status is `SUCCESS`
- `raw_text` contains a substantive answer
- `latency_ms` is reasonable

---

## Step 5: Enable in Config

Set `enabled: true` in `config/engines.yaml` once the integration is verified.

---

## Step 6: Update Engine Querying Skill

Final step: ensure `skills/engine_querying.md` has an entry for the new engine.

## Adding a Browser-Based Engine

The process is similar but the `query_with_browser()` method in `tools/browser_agent.py` must be extended:

1. Add selector to `SELECTORS` dict:
   ```python
   SELECTORS = {
       ...,
       "new_browser_engine": ".response-container-class",  # verify before use
   }
   ```

2. Add URL mapping in `_engine_url()`:
   ```python
   urls = {
       ...,
       "new_browser_engine": "https://newengine.com/search",
   }
   ```

3. Test with Playwright:
   ```python
   from tools.browser_agent import BrowserAgent
   agent = BrowserAgent()
   result = agent.query(engine="new_browser_engine", prompt="test query")
   print(result)
   ```

4. Update `config/engines.yaml` with the confirmed `wait_selector` value.
