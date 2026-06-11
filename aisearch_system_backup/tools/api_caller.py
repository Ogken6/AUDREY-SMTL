#!/usr/bin/env python3
"""
api_caller.py — Unified API interface for all AI engines
Handles: ChatGPT, Perplexity, Gemini, Claude
"""

import os
import time
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)

ENGINE_CONFIGS = {
    "chatgpt": {
        "provider": "openai",
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
        "endpoint": "https://api.openai.com/v1/chat/completions",
    },
    "perplexity": {
        "provider": "perplexity",
        "model": "llama-3.1-sonar-large-128k-online",
        "api_key_env": "PERPLEXITY_API_KEY",
        "endpoint": "https://api.perplexity.ai/chat/completions",
    },
    "gemini": {
        "provider": "google",
        "model": "gemini-2.0-flash-exp",
        "api_key_env": "GEMINI_API_KEY",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
    },
    "claude": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "api_key_env": "ANTHROPIC_API_KEY",
        "endpoint": "https://api.anthropic.com/v1/messages",
    },
}

class APICaller:
    """
    Unified LLM API caller for all AI engines and internal processing calls.
    """

    def __init__(self):
        self.retry_backoff = [10, 30, 90]  # seconds

    def query_engine(
        self,
        engine: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1500,
        region: Optional[str] = None,
    ) -> dict:
        """
        Query an external AI engine (FALCON's primary interface).
        Returns dict with status, raw_text, model, latency_ms, error.
        """
        import requests
        config = ENGINE_CONFIGS.get(engine)
        if not config:
            return {"status": "ERROR", "error": f"Unknown engine: {engine}"}

        api_key = os.environ.get(config["api_key_env"])
        if not api_key:
            return {"status": "ERROR", "error": f"API key not set: {config['api_key_env']}"}

        headers = self._headers(engine, api_key)
        payload = self._payload(engine, config, prompt, system_prompt, temperature, max_tokens)
        proxies = self._proxies(region) if region else None

        start = time.time()
        for attempt, backoff_sec in enumerate(self.retry_backoff):
            try:
                resp = requests.post(
                    config["endpoint"],
                    headers=headers,
                    json=payload,
                    proxies=proxies,
                    timeout=30,
                )
                latency_ms = int((time.time() - start) * 1000)

                if resp.status_code == 429:
                    if attempt < len(self.retry_backoff) - 1:
                        time.sleep(backoff_sec)
                        continue
                    return {"status": "RATE_LIMITED", "error": "429", "latency_ms": latency_ms}

                if resp.status_code >= 500:
                    if attempt < len(self.retry_backoff) - 1:
                        time.sleep(5)
                        continue
                    return {"status": "ERROR", "error": f"HTTP {resp.status_code}", "latency_ms": latency_ms}

                if resp.status_code != 200:
                    return {"status": "ERROR", "error": f"HTTP {resp.status_code}",
                            "latency_ms": latency_ms}

                raw_text = self._parse_response(engine, resp)
                return {
                    "status": "SUCCESS",
                    "raw_text": raw_text,
                    "model": config["model"],
                    "latency_ms": latency_ms,
                }

            except Exception as e:
                if attempt < len(self.retry_backoff) - 1:
                    time.sleep(5)
                    continue
                return {"status": "ERROR", "error": str(e), "latency_ms": int((time.time() - start) * 1000)}

    def internal_call(
        self,
        purpose: str,
        content: str,
        output_format: str = "json",
        max_tokens: int = 1000,
        brand: Optional[str] = None,
    ) -> dict:
        """
        Internal LLM call for SIEVE extraction and ORACLE-X recommendation generation.
        Maps purpose to the correct prompt and routes to the best internal model.
        """
        purpose_prompts = {
            "extraction": "memory/prompts/extraction_prompt.md",
            "sentiment": "memory/prompts/sentiment_prompt.md",
            "recommendation": "memory/prompts/recommendation_prompt.md",
            "gap_analysis": "memory/prompts/gap_analysis_prompt.md",
        }
        prompt_path = purpose_prompts.get(purpose, "memory/prompts/extraction_prompt.md")

        system_prompt = self._load_system_prompt(prompt_path)
        user_content = f"Task content:\n{content}"
        if brand:
            user_content += f"\n\nTarget brand: {brand}"

        return self.query_engine(
            engine="chatgpt",
            prompt=user_content,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=max_tokens,
        )

    def _headers(self, engine: str, api_key: str) -> dict:
        if engine == "chatgpt":
            return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        elif engine == "perplexity":
            return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        elif engine == "gemini":
            return {"X-Goog-API-Key": api_key, "Content-Type": "application/json"}
        elif engine == "claude":
            return {"x-api-key": api_key, "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"}

    def _payload(self, engine, config, prompt, system_prompt, temperature, max_tokens):
        messages = []
        if system_prompt and engine != "claude":
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if engine == "chatgpt":
            return {"model": config["model"], "messages": messages,
                    "max_tokens": max_tokens, "temperature": temperature}
        elif engine == "perplexity":
            return {"model": config["model"], "messages": messages,
                    "max_tokens": max_tokens, "temperature": temperature}
        elif engine == "gemini":
            full_prompt = (system_prompt + "\n\n" + prompt) if system_prompt else prompt
            return {"contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature}}
        elif engine == "claude":
            return {"model": config["model"], "messages": messages,
                    "max_tokens": max_tokens, "temperature": temperature,
                    "system": system_prompt or "You are a helpful assistant."}

    def _parse_response(self, engine: str, resp) -> str:
        if engine == "chatgpt":
            return resp.json()["choices"][0]["message"]["content"]
        elif engine == "perplexity":
            return resp.json()["choices"][0]["message"]["content"]
        elif engine == "gemini":
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        elif engine == "claude":
            return resp.json()["content"][0]["text"]

    def _proxies(self, region: str) -> Optional[dict]:
        api_key = os.environ.get("PROXY_API_KEY")
        if not api_key:
            return None
        proxy_url = f"http://{region}-proxy:{api_key}@proxy.example.com:8080"
        return {"http": proxy_url, "https": proxy_url}

    def _load_system_prompt(self, prompt_path: str) -> str:
        """Load a prompt template from disk."""
        import os
        base = "/root/.openclaw/workspace/aisearch_system"
        full_path = os.path.join(base, prompt_path.replace("memory/", ""))
        if os.path.exists(full_path):
            with open(full_path) as f:
                return f.read()
        return "You are a helpful data extraction assistant."
