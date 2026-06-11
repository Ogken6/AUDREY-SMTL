#!/usr/bin/env python3
"""
browser_agent.py — Headless browser query tool for FALCON
For AI engines that require JavaScript rendering: Google AIO, Google AI Mode, Copilot.
Also used by CARTOGRAPHER for URLs requiring JS to extract content.
"""

import os
import random
import time
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Selector registry — update when pages change
SELECTORS = {
    "google_aio": ".IVvmHb",        # Google AI Overview container
    "google_aim": ".SGE-response", # Google AI Mode
    "copilot": ".cib-chat-main",  # Copilot response container
}

class BrowserAgent:
    """
    Headless browser agent for querying non-API AI engines.
    """

    def __init__(
        self,
        proxy: Optional[dict] = None,
        session_profile: str = "clean",
        headless: bool = True,
    ):
        self.proxy = proxy
        self.session_profile = session_profile
        self.headless = headless
        self._playwright = None

    def query(
        self,
        engine: str,
        prompt: str,
        wait_for_selector: Optional[str] = None,
        timeout_ms: int = 15000,
        screenshot: bool = False,
    ) -> dict:
        """
        Query an AI engine via headless browser.
        Returns dict with raw_text, cited_urls, aio_present, render_time_ms, status, error.
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {"status": "error", "error": "Playwright not installed: pip install playwright",
                    "raw_text": None, "cited_urls": [], "aio_present": None}

        wait_for_selector = wait_for_selector or SELECTORS.get(engine)
        start_ms = int(time.time() * 1000)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                locale="en-GB",
                ignore_https_errors=True,
                proxy=self.proxy,
            )
            page = context.new_page()

            try:
                engine_url = self._engine_url(engine)
                page.goto(engine_url, timeout=30000, wait_until="networkidle")

                # Inject query
                query_input = self._find_query_input(page, engine)
                if query_input:
                    query_input.fill(prompt)
                    page.keyboard.press("Enter")

                    if wait_for_selector:
                        try:
                            page.wait_for_selector(wait_for_selector, timeout=20000)
                        except Exception:
                            pass  # Selector not found — AIO may not have triggered

                    page.wait_for_load_state("networkidle", timeout=20000)

                # Random delay to avoid bot detection
                page.wait_for_timeout(random.uniform(1000, 3000))

                raw_text = page.inner_text("body")
                cited_urls = self._extract_cited_urls(page, engine)
                aio_present = self._check_aio_present(page, wait_for_selector)
                render_time_ms = int(time.time() * 1000) - start_ms
                screenshot_b64 = None

                if screenshot:
                    screenshot_b64 = page.screenshot()

                return {
                    "status": "success",
                    "raw_text": raw_text,
                    "cited_urls": cited_urls,
                    "aio_present": aio_present,
                    "render_time_ms": render_time_ms,
                    "screenshot_b64": screenshot_b64,
                }

            except Exception as e:
                render_time_ms = int(time.time() * 1000) - start_ms
                return {
                    "status": "error",
                    "error": str(e),
                    "raw_text": None,
                    "cited_urls": [],
                    "aio_present": False,
                    "render_time_ms": render_time_ms,
                }
            finally:
                browser.close()

    def fetch(self, url: str) -> dict:
        """Fetch a URL with full JS rendering (used by CARTOGRAPHER)."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {"status": "error", "error": "Playwright not installed"}
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, timeout=30000, wait_until="networkidle")
                raw_text = page.inner_text("body")
                title = page.title()
                domain = urlparse(url).netloc
                return {"status": "success", "raw_text": raw_text, "title": title,
                        "domain": domain, "url": url}
            except Exception as e:
                return {"status": "error", "error": str(e), "url": url}
            finally:
                browser.close()

    def _engine_url(self, engine: str) -> str:
        urls = {
            "google_aio": "https://www.google.com/search?q=ai+overview",
            "google_aim": "https://www.google.com/search?q=ai+mode",
            "copilot": "https://copilot.microsoft.com",
        }
        return urls.get(engine, "https://www.google.com/search?q=test")

    def _find_query_input(self, page, engine: str):
        selectors = ["textarea[name='q']", "input[name='q']",
                      "[role='searchbox']", "textarea.generated-input"]
        for sel in selectors:
            try:
                el = page.query_selector(sel)
                if el:
                    return el
            except Exception:
                continue
        return None

    def _extract_cited_urls(self, page, engine: str) -> list:
        urls = []
        try:
            links = page.query_selector_all("a[href]")
            for a in links:
                href = a.get_attribute("href") or ""
                if href.startswith("http") and "javascript" not in href.lower():
                    urls.append(href)
        except Exception:
            pass
        return list(dict.fromkeys(urls))

    def _check_aio_present(self, page, selector: str) -> bool:
        try:
            page.query_selector(selector)
            return True
        except Exception:
            return False
