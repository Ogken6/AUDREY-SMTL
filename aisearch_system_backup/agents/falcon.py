#!/usr/bin/env python3
"""
falcon.py — ORACLE Engine Query Interface
Handles all outbound queries to AI search engines.
Supports both API-based (ChatGPT, Perplexity, Gemini, Claude)
and browser-based (Google AIO, AI Mode, Copilot) engines.
Usage:
    python agents/falcon.py --engine=perplexity --prompt="best recipe websites UK"
    python agents/falcon.py --test-all
"""

import os
import sys
import json
import time
import random
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.api_caller import APICaller
from tools.browser_agent import BrowserAgent
from tools.proxy_manager import ProxyManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger("falcon")

class Falcon:
    """
    FALCON is ORACLE's outbound query interface.
    It does not modify raw response data — it captures and returns it exactly as received.
    Rate limit handling: exponential backoff, max 5 retries.
    Personalisation detection: flags responses that may be personalised.
    """

    def __init__(self):
        self.api = APICaller()
        self.browser = BrowserAgent()
        self.proxy = ProxyManager()

    def query(self, engine: str, prompt: str, model: str = None,
              temperature: float = 0.3, max_tokens: int = 1500) -> dict:
        """
        Query a single engine with a prompt.
        Returns full response dict with status, raw_text, latency_ms.
        """
        import yaml
        with open(PROJECT_ROOT / "config" / "engines.yaml") as f:
            eng_cfg = yaml.safe_load(f).get("engines", {}).get(engine, {})

        access_method = eng_cfg.get("access_method", "api")
        region = eng_cfg.get("proxy_region", "eu-west")

        if access_method == "browser":
            return self._query_browser(engine, prompt, region)
        else:
            return self._query_api(engine, prompt, model, temperature, max_tokens, region)

    def _query_api(self, engine: str, prompt: str, model, temperature,
                   max_tokens, region) -> dict:
        """Query an API-based engine (ChatGPT, Perplexity, Gemini, Claude)."""
        proxy = self.proxy.get_proxy(region) if region != "none" else None

        result = self.api.query_engine(
            engine=engine,
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            session_id=f"falcon_{int(time.time())}",
            region=region,
        )

        # FALCON never modifies raw_text — pass through exactly
        result["query_engine"] = engine
        result["query_prompt"] = prompt
        result["queried_at"] = datetime.now(timezone.utc).isoformat()

        # Detect personalisation signals
        result["personalisation_detected"] = self._detect_personalisation(result)

        return result

    def _query_browser(self, engine: str, prompt: str, region: str) -> dict:
        """Query a browser-based engine (Google AIO, AI Mode, Copilot)."""
        result = self.browser.query(engine=engine, prompt=prompt)
        result["query_engine"] = engine
        result["query_prompt"] = prompt
        result["queried_at"] = datetime.now(timezone.utc).isoformat()
        result["personalisation_detected"] = self._detect_personalisation(result)
        return result

    def _detect_personalisation(self, result: dict) -> bool:
        """
        Flag possible personalisation in responses.
        Signals: location-specific content, session references, personalised pronouns.
        FALCON detects and flags — does not correct or compensate.
        """
        raw = result.get("raw_text", "").lower()
        signals = [
            "near you", "around you", "in your area",
            "based on your search history", "since you searched",
            "your location", "your preferences",
            "previously viewed", "you might like",
        ]
        for signal in signals:
            if signal in raw:
                logger.warning(f"Personalisation signal detected in {result.get('query_engine')}")
                return True
        return False

    def test_all_engines(self, test_prompt: str = "best recipe websites UK 2026") -> dict:
        """Test connectivity and response quality for all enabled engines."""
        import yaml
        with open(PROJECT_ROOT / "config" / "engines.yaml") as f:
            all_engines = yaml.safe_load(f).get("engines", {})

        results = {}
        for engine, cfg in all_engines.items():
            if not cfg.get("enabled", True):
                continue
            logger.info(f"Testing engine: {engine}")
            try:
                result = self.query(engine=engine, prompt=test_prompt)
                results[engine] = {
                    "status": result.get("status"),
                    "latency_ms": result.get("latency_ms"),
                    "raw_text_length": len(result.get("raw_text", "")),
                    "personalisation_detected": result.get("personalisation_detected"),
                    "error": result.get("error"),
                }
            except Exception as e:
                results[engine] = {"status": "ERROR", "error": str(e)}

        return results


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORACLE FALCON — Engine Query Interface")
    parser.add_argument("--engine", help="Engine to query (e.g. perplexity, chatgpt)")
    parser.add_argument("--prompt", help="Prompt text to send")
    parser.add_argument("--test-all", action="store_true", help="Test all enabled engines")
    parser.add_argument("--model", help="Model override")
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--max-tokens", type=int, default=1500)
    args = parser.parse_args()

    falcon = Falcon()

    if args.test_all:
        results = falcon.test_all_engines()
        print(json.dumps(results, indent=2))
    elif args.engine and args.prompt:
        result = falcon.query(
            engine=args.engine,
            prompt=args.prompt,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()