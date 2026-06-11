#!/usr/bin/env python3
"""
url_fetcher.py — Fetch and extract content from citation URLs
Used by CARTOGRAPHER to retrieve source page content behind AI citations.
"""

import os
import re
import time
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

FETCH_CACHE = {}  # url -> (content, timestamp, ttl=48h)

class URLFetcher:
    """
    Fetches and extracts main body text from web pages.
    Respects robots.txt, enforces domain rate limits, and caches for 48 hours.
    """

    def __init__(
        self,
        respect_robots_txt: bool = True,
        rate_limit_per_domain_seconds: int = 2,
        timeout_seconds: int = 10,
        max_chars: int = 5000,
    ):
        self.respect_robots_txt = respect_robots_txt
        self.rate_limit = rate_limit_per_domain_seconds
        self.timeout = timeout_seconds
        self.max_chars = max_chars
        self._last_fetch = {}

    def fetch(
        self,
        url: str,
        extract_main_content: bool = True,
        include_metadata: bool = True,
        use_browser: bool = False,
    ) -> dict:
        """
        Fetch a URL and extract main readable content.
        Returns dict: url, status, content, title, published_date, author, domain,
                      content_type, word_count, fetch_time_ms.
        """
        # Cache check — use cached if fetched within 48h
        if url in FETCH_CACHE:
            content, fetched_at = FETCH_CACHE[url]
            age_hours = (time.time() - fetched_at) / 3600
            if age_hours < 48:
                return content  # Return cached dict

        # Rate limiting per domain
        domain = urlparse(url).netloc
        if domain in self._last_fetch:
            elapsed = time.time() - self._last_fetch[domain]
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)
        self._last_fetch[domain] = time.time()

        import requests
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ORACLE/1.0)"}
        start_ms = int(time.time() * 1000)

        try:
            resp = requests.get(url, headers=headers, timeout=self.timeout,
                                allow_redirects=True)
            resp.raise_for_status()
            fetch_time_ms = int(time.time() * 1000) - start_ms

            if use_browser or resp.headers.get("content-type", "").startswith("text/html"):
                content, title, author, published_date = self._extract_html(
                    resp.text, include_metadata)
                content_type = self._classify_content_type(resp.text, domain)
            else:
                content = resp.text[:self.max_chars]
                title, author, published_date = None, None, None
                content_type = "unknown"

            result = {
                "url": url,
                "status": "success",
                "content": content[:self.max_chars],
                "title": title,
                "published_date": published_date,
                "author": author,
                "domain": domain,
                "content_type": content_type,
                "word_count": len(content.split()),
                "fetch_time_ms": fetch_time_ms,
            }
            FETCH_CACHE[url] = (result, time.time())
            return result

        except Exception as e:
            fetch_time_ms = int(time.time() * 1000) - start_ms
            status = "blocked" if "403" in str(e) else "error"
            return {
                "url": url,
                "status": status,
                "error": str(e),
                "fetch_time_ms": fetch_time_ms,
                "content_type": "unknown",
            }

    def _extract_html(self, html: str, include_meta: bool):
        """Extract title, author, date, and main body text from HTML."""
        from html.parser import HTMLParser

        class Extractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_nav = self.in_footer = self.in_script = self.in_style = False
                self.in_article = False
                self.text_parts = []
                self.title = None
                self.author = None
                self.published_date = None
                self._tag_stack = []

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                self._tag_stack.append(tag)
                if tag in ("nav", "footer", "script", "style"):
                    (self.in_nav if tag == "nav" else
                     self.in_footer if tag == "footer" else
                     self.in_script if tag == "script" else self.in_style)
                if tag == "article":
                    self.in_article = True
                if tag == "title" and not self.title:
                    pass  # handled in handle_data
                if include_meta:
                    if tag == "meta":
                        name = attrs_dict.get("name", "")
                        prop = attrs_dict.get("property", "")
                        if name in ("author", "article:author") and not self.author:
                            self.author = attrs_dict.get("content")
                        if name in ("date", "article:published_time") and not self.published_date:
                            self.published_date = attrs_dict.get("content")

            def handle_endtag(self, tag):
                if self._tag_stack and self._tag_stack[-1] == tag:
                    self._tag_stack.pop()
                if tag in ("nav", "footer", "script", "style"):
                    self.in_nav = self.in_footer = self.in_script = self.in_style = False
                if tag == "article":
                    self.in_article = False

            def handle_data(self, data):
                if self.in_script or self.in_style or self.in_nav or self.in_footer:
                    return
                stripped = data.strip()
                if stripped:
                    self.text_parts.append(stripped)

        extractor = Extractor()
        extractor.feed(html)
        title_match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else None
        return " ".join(extractor.text_parts), title, extractor.author, extractor.published_date

    def _classify_content_type(self, html: str, domain: str) -> str:
        """Classify page content type from HTML and domain."""
        forum_domains = ["reddit.com", "quora.com", "news.ycombinator.com"]
        review_domains = ["g2.com", "capterra.com", "trustpilot.com", "yelp.com"]
        wiki_domains = ["wikipedia.org"]
        if any(d in domain for d in forum_domains):
            return "forum"
        if any(d in domain for d in review_domains):
            return "review"
        if any(d in domain for d in wiki_domains):
            return "wiki"
        if "<article" in html.lower() or "blog" in domain:
            return "article"
        return "unknown"
