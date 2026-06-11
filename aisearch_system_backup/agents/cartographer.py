#!/usr/bin/env python3
"""
cartographer.py — ORACLE Citation Tracking Agent
Builds and maintains the citation graph: tracks which sources are cited
by which engines in response to which prompts.
Also fetches and stores source content for high-influence sources.
Usage:
    python agents/cartographer.py --update-graph
    python agents/cartographer.py --fetch-sources --run-id=run_20260527
"""

import os
import sys
import json
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.url_fetcher import URLFetcher
from tools.db_writer import DBWriter

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger("cartographer")

GRAPH_PATH = PROJECT_ROOT / "memory" / "citation_graph.json"
EXTRACTIONS_IN_PATH = PROJECT_ROOT / "memory" / "extractions"

class Cartographer:
    """
    CARTOGRAPHER builds and maintains the citation graph.
    Key principle: FALCON never modifies raw response data.
    CARTOGRAPHER only reads from extraction records (SIEVE output).
    """

    def __init__(self):
        self.fetcher = URLFetcher()
        self.db = DBWriter()
        self.graph = self._load_graph()

    def _load_graph(self) -> dict:
        if GRAPH_PATH.exists():
            with open(GRAPH_PATH) as f:
                return json.load(f)
        return {
            "nodes": {},      # url -> {domain, source_type, influence_score, last_updated}
            "edges": [],      # {source_url, target_engine, target_prompt, cited_at, brand_cited}
            "stats": {
                "total_sources": 0,
                "total_citations": 0,
                "engines_citing": {},
                "domains_citing": {},
            }
        }

    def _save_graph(self):
        with open(GRAPH_PATH, "w") as f:
            json.dump(self.graph, f, indent=2)

    def _estimate_influence(self, url: str) -> float:
        """
        Estimate source influence score based on domain signals.
        Higher scores = more cited across the graph.
        """
        domain = url.split("/")[2] if "://" in url else url
        known_domains = {
            "wikipedia.org": 0.9,
            "github.com": 0.85,
            "medium.com": 0.7,
            "stackoverflow.com": 0.8,
            "zdnet.com": 0.6,
            "techcrunch.com": 0.75,
            "theverge.com": 0.7,
            "nytimes.com": 0.85,
            "bbc.com": 0.8,
            "theguardian.com": 0.8,
            "reddit.com": 0.65,
            "youtube.com": 0.7,
        }
        for d, score in known_domains.items():
            if d in domain:
                return score
        return 0.5  # Default for unknown domains

    def _infer_source_type(self, url: str) -> str:
        """Infer source type from URL patterns."""
        url_lower = url.lower()
        if "github.com" in url:
            return "code_repository"
        elif "stackoverflow.com" in url:
            return "q_and_a"
        elif "medium.com" in url or "blog" in url:
            return "blog"
        elif any(k in url_lower for k in [".pdf", "whitepaper", "report"]):
            return "report"
        elif any(k in url_lower for k in ["news", "article", "bbc", "guardian", "nytimes"]):
            return "news"
        elif any(k in url_lower for k in ["youtube.com", "youtu.be"]):
            return "video"
        else:
            return "unknown"

    # ── Graph Building ────────────────────────────────────────────────────────

    def update_graph_from_extractions(self, extractions: list = None) -> dict:
        """
        Update the citation graph from SIEVE extraction records.
        Each extraction contains cited_urls from the AI response.
        """
        if extractions is None:
            extractions = self._load_latest_extractions()

        logger.info(f"CARTOGRAPHER updating graph from {len(extractions)} extractions")

        new_nodes = 0
        new_edges = 0

        for ext in extractions:
            if ext.get("processing_status") == "error":
                continue

            engine = ext.get("engine", "unknown")
            prompt_id = ext.get("prompt_id", "unknown")
            run_id = ext.get("run_id", "unknown")
            cited_urls = ext.get("cited_urls", [])
            brand_cited = ext.get("brand_present", False)
            captured_at = ext.get("captured_at", datetime.now(timezone.utc).isoformat())

            for url in cited_urls:
                # Add/update node
                if url not in self.graph["nodes"]:
                    self.graph["nodes"][url] = {
                        "domain": url.split("/")[2] if "://" in url else url,
                        "source_type": self._infer_source_type(url),
                        "influence_score": self._estimate_influence(url),
                        "first_seen": captured_at,
                        "last_updated": captured_at,
                        "citation_count": 0,
                        "engines_citing": [],
                        "prompts_citing": [],
                    }
                    new_nodes += 1

                node = self.graph["nodes"][url]
                node["citation_count"] += 1
                node["last_updated"] = captured_at

                if engine not in node["engines_citing"]:
                    node["engines_citing"].append(engine)

                if prompt_id not in node["prompts_citing"]:
                    node["prompts_citing"].append(prompt_id)

                # Add edge
                edge = {
                    "source_url": url,
                    "target_engine": engine,
                    "target_prompt_id": prompt_id,
                    "target_run_id": run_id,
                    "brand_cited": brand_cited,
                    "cited_at": captured_at,
                }
                self.graph["edges"].append(edge)
                new_edges += 1

        # Update stats
        self.graph["stats"]["total_sources"] = len(self.graph["nodes"])
        self.graph["stats"]["total_citations"] = len(self.graph["edges"])

        self._save_graph()

        logger.info(f"CARTOGRAPHER graph update complete: {new_nodes} new nodes, {new_edges} new edges")
        return {
            "new_nodes": new_nodes,
            "new_edges": new_edges,
            "total_sources": self.graph["stats"]["total_sources"],
            "total_citations": self.graph["stats"]["total_citations"],
        }

    def _load_latest_extractions(self) -> list:
        """Load the most recent extraction file."""
        if not EXTRACTIONS_IN_PATH.exists():
            return []
        files = sorted(EXTRACTIONS_IN_PATH.glob("extractions_*.json"), reverse=True)
        if not files:
            return []
        with open(files[0]) as f:
            return json.load(f)

    # ── Source Content Fetching ──────────────────────────────────────────────

    def fetch_high_influence_sources(self, min_influence: float = 0.7,
                                     max_sources: int = 20) -> list:
        """
        Fetch content from high-influence sources in the graph.
        Used for ORACLE-X to understand what content competitors are
        using to back their recommendations.
        """
        sources = [
            {"url": url, **node}
            for url, node in self.graph["nodes"].items()
            if node.get("influence_score", 0) >= min_influence
        ]
        sources.sort(key=lambda x: x["influence_score"], reverse=True)
        sources = sources[:max_sources]

        logger.info(f"CARTOGRAPHER fetching content from {len(sources)} high-influence sources")

        fetched = []
        for src in sources:
            try:
                content = self.fetcher.fetch(url=src["url"])
                src["fetch_status"] = "success"
                src["content_length"] = len(content) if content else 0
                src["content_preview"] = content[:500] if content else ""
                fetched.append(src)
            except Exception as e:
                src["fetch_status"] = "error"
                src["fetch_error"] = str(e)
                fetched.append(src)

        return fetched

    # ── Competitive Citation Analysis ───────────────────────────────────────

    def competitor_citation_sources(self, competitor_name: str) -> list:
        """
        Find all sources used to cite a specific competitor.
        Returns sources ranked by citation frequency for that competitor.
        """
        competitor_edges = [
            e for e in self.graph["edges"]
            if competitor_name.lower() in e.get("source_url", "").lower()
        ]
        source_counts = defaultdict(int)
        for edge in competitor_edges:
            source_counts[edge["source_url"]] += 1

        return sorted(
            [{"url": url, "citation_count": count} for url, count in source_counts.items()],
            key=lambda x: x["citation_count"],
            reverse=True,
        )

    # ── Graph Statistics ─────────────────────────────────────────────────────

    def graph_stats(self) -> dict:
        """Return current citation graph statistics."""
        return self.graph.get("stats", {})

    def top_sources(self, limit: int = 20) -> list:
        """Return top N most-cited sources by citation count."""
        nodes = self.graph.get("nodes", {})
        return sorted(
            [{"url": url, **node} for url, node in nodes.items()],
            key=lambda x: x.get("citation_count", 0),
            reverse=True,
        )[:limit]

    def sources_for_engine(self, engine: str) -> list:
        """Get all sources cited by a specific engine."""
        edges = self.graph.get("edges", [])
        urls = set(e["source_url"] for e in edges if e.get("target_engine") == engine)
        return [self.graph["nodes"].get(url, {"url": url}) for url in urls]


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORACLE CARTOGRAPHER — Citation Tracking")
    parser.add_argument("--update-graph", action="store_true", help="Update citation graph from extractions")
    parser.add_argument("--fetch-sources", action="store_true", help="Fetch high-influence source content")
    parser.add_argument("--run-id", help="Run ID for extraction source")
    parser.add_argument("--top-sources", type=int, help="Show top N most-cited sources")
    parser.add_argument("--competitor", help="Show citation sources for a competitor")
    parser.add_argument("--stats", action="store_true", help="Show citation graph stats")
    args = parser.parse_args()

    cartographer = Cartographer()

    if args.update_graph:
        result = cartographer.update_graph_from_extractions()
        print(json.dumps(result, indent=2))

    elif args.fetch_sources:
        sources = cartographer.fetch_high_influence_sources()
        print(json.dumps(sources[:10], indent=2))

    elif args.top_sources:
        top = cartographer.top_sources(limit=args.top_sources)
        for s in top:
            print(f"  [{s.get('influence_score', 0):.2f}] {s.get('url', 'unknown')}")

    elif args.competitor:
        sources = cartographer.competitor_citation_sources(args.competitor)
        print(json.dumps(sources, indent=2))

    elif args.stats:
        print(json.dumps(cartographer.graph_stats(), indent=2))

    else:
        parser.print_help()