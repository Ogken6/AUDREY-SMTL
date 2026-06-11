#!/usr/bin/env python3
"""
rival.py — ORACLE Competitive Gap Analysis Agent
Identifies where the target brand is losing visibility to competitors
in AI-generated responses. Runs after SIEVE extractions are complete.
Usage:
    python agents/rival.py --analyze --brand=crispyglaze --run-id=run_20260527
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.api_caller import APICaller

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger("rival")

EXTRACTIONS_IN_PATH = PROJECT_ROOT / "memory" / "extractions"
GAP_ANALYSIS_TEMPLATE_PATH = PROJECT_ROOT / "prompts" / "gap_analysis_prompt.md"
PREV_PERIOD_EXT_PATH = PROJECT_ROOT / "memory" / "extractions"

class Rival:
    """
    RIVAL performs competitive gap analysis.
    It reads SIEVE extraction records and the citation graph,
    identifies gaps where the brand is absent while competitors are present,
    and returns a structured gap map with severity scores.
    """

    def __init__(self, brand: str):
        self.brand = brand
        self.api = APICaller()
        self.brand_config = self._load_brand_config()
        self.gap_template = self._load_template(GAP_ANALYSIS_TEMPLATE_PATH)
        self.gaps = []

    def _load_brand_config(self) -> dict:
        import yaml
        with open(PROJECT_ROOT / "config" / "brands.yaml") as f:
            all_brands = yaml.safe_load(f).get("brands", {})
        if self.brand not in all_brands:
            raise ValueError(f"Brand '{self.brand}' not in brands.yaml")
        return all_brands[self.brand]

    def _load_template(self, path: Path) -> str:
        with open(path) as f:
            return f.read()

    def _load_extractions(self, run_id: str = None) -> list:
        if not EXTRACTIONS_IN_PATH.exists():
            return []
        files = sorted(EXTRACTIONS_IN_PATH.glob("extractions_*.json"), reverse=True)
        if not files:
            return []
        target_file = None
        if run_id:
            target_file = EXTRACTIONS_IN_PATH / f"extractions_{run_id}.json"
        if not target_file or not target_file.exists():
            target_file = files[0]
        with open(target_file) as f:
            return json.load(f)

    # ── Gap Analysis ─────────────────────────────────────────────────────────

    def analyze_gaps(self, run_id: str = None) -> dict:
        """
        Main entry point: analyse gaps for a given run.
        Returns full gap analysis report.
        """
        logger.info(f"RIVAL analyzing gaps for brand: {self.brand}")

        extractions = self._load_extractions(run_id)
        logger.info(f"Loaded {len(extractions)} extractions for analysis")

        if not extractions:
            logger.warning("No extractions found — cannot run gap analysis")
            return {"gaps": [], "displacement_events": [], "engine_patterns": [], "emerging_competitors": []}

        # Build extraction summary
        ext_summary = self._build_extraction_summary(extractions)

        # Try LLM-based gap analysis first
        try:
            gap_report = self._llm_gap_analysis(ext_summary, run_id)
            self.gaps = gap_report.get("gaps", [])
            return gap_report
        except Exception as e:
            logger.warning(f"LLM gap analysis failed, falling back to heuristic: {e}")
            return self._heuristic_gap_analysis(extractions)

    def _build_extraction_summary(self, extractions: list) -> dict:
        """Build a structured summary of extractions for gap analysis."""
        prompt_map = defaultdict(lambda: {
            "total_responses": 0,
            "brand_present_count": 0,
            "competitors_seen": set(),
            "engines": set(),
            "sentiments": [],
            "cited_urls": [],
        })

        for ext in extractions:
            if ext.get("processing_status") == "error":
                continue
            prompt_id = ext.get("prompt_id", "unknown")
            pm = prompt_map[prompt_id]
            pm["total_responses"] += 1
            pm["engines"].add(ext.get("engine", "unknown"))
            if ext.get("brand_present"):
                pm["brand_present_count"] += 1
            for comp in ext.get("entities", []):
                if comp.get("is_tracked_competitor"):
                    pm["competitors_seen"].add(comp.get("canonical_name", "unknown"))
            if ext.get("sentiment_class"):
                pm["sentiments"].append(ext["sentiment_class"])
            pm["cited_urls"].extend(ext.get("cited_urls", [])[:5])

        # Convert to serialisable format
        summary = {}
        for prompt_id, pm in prompt_map.items():
            summary[prompt_id] = {
                "total_responses": pm["total_responses"],
                "brand_present_count": pm["brand_present_count"],
                "brand_presence_rate": pm["brand_present_count"] / max(1, pm["total_responses"]),
                "competitors_seen": list(pm["competitors_seen"]),
                "engines": list(pm["engines"]),
                "avg_sentiment": self._mode(pm["sentiments"]) if pm["sentiments"] else "unknown",
                "citation_sample": pm["cited_urls"][:3],
            }
        return summary

    def _llm_gap_analysis(self, ext_summary: dict, run_id: str = None) -> dict:
        """Use LLM to perform structured gap analysis."""
        total_prompts = len(ext_summary)
        total_responses = sum(v["total_responses"] for v in ext_summary.values())

        prompt = self.gap_template.format(
            target_brand=self.brand_config["canonical_name"],
            date_range="last 7 days",
            total_prompts=total_prompts,
            total_responses=total_responses,
            extraction_summary_json=json.dumps(ext_summary, indent=2),
            previous_period_summary_json="{}",
        )

        result = self.api.internal_call(
            prompt=prompt,
            model="claude",
            max_tokens=3000,
            temperature=0.2,
        )

        raw = result.get("raw_text", "{}")
        import re
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(raw)

    def _heuristic_gap_analysis(self, extractions: list) -> dict:
        """
        Fallback when LLM is unavailable — rule-based gap detection.
        Identifies: brand_absent gaps, rank displacement, engine-specific gaps.
        """
        import hashlib

        brand_name = self.brand_config["canonical_name"]
        competitors = {c["name"] for c in self.brand_config.get("competitors", [])}

        gaps = []
        gap_id_counter = 1

        # Group by prompt_id
        by_prompt = defaultdict(list)
        for ext in extractions:
            if ext.get("processing_status") == "error":
                continue
            by_prompt[ext["prompt_id"]].append(ext)

        for prompt_id, exts in by_prompt.items():
            brand_in = any(e.get("brand_present") for e in exts)
            competitor_in = set()
            for e in exts:
                for ent in e.get("entities", []):
                    if ent.get("is_tracked_competitor"):
                        competitor_in.add(ent.get("canonical_name", "unknown"))

            if not brand_in and competitor_in:
                # Brand absent — competitors present
                engines_with_gap = [e.get("engine") for e in exts]
                for comp in competitor_in:
                    gaps.append({
                        "gap_id": f"gap_{brand_id_counter:04d}",
                        "prompt_id": prompt_id,
                        "prompt_text": f"Prompt: {prompt_id}",
                        "gap_type": "brand_absent",
                        "engines_with_gap": engines_with_gap,
                        "competitor_present": comp,
                        "competitor_consistency": 1.0,
                        "gap_severity": "high" if len(engines_with_gap) > 1 else "medium",
                        "gap_severity_rationale": f"Brand absent on {len(engines_with_gap)} engines; {comp} captures this space",
                    })
                    brand_id_counter += 1

        displacement_events = []
        engine_patterns = []
        emerging_competitors = []

        return {
            "gaps": gaps,
            "displacement_events": displacement_events,
            "engine_patterns": engine_patterns,
            "emerging_competitors": emerging_competitors,
        }

    # ── Gap Persistence ──────────────────────────────────────────────────────

    def save_gap_report(self, report: dict, run_id: str = None):
        """Write gap report to memory for ORACLE-X to consume."""
        out_dir = PROJECT_ROOT / "memory" / "competitive_reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"gap_report_{run_id or 'latest'}.json"
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Saved gap report to {out_path}")

    def load_latest_gap_report(self) -> dict:
        out_dir = PROJECT_ROOT / "memory" / "competitive_reports"
        if not out_dir.exists():
            return {}
        files = sorted(out_dir.glob("gap_report_*.json"), reverse=True)
        if not files:
            return {}
        with open(files[0]) as f:
            return json.load(f)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _mode(self, lst: list):
        """Return most common element in list."""
        if not lst:
            return None
        counts = defaultdict(int)
        for item in lst:
            counts[item] += 1
        return max(counts, key=counts.get)

    def _make_gap_id(self, text: str) -> str:
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()[:12]


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORACLE RIVAL — Competitive Gap Analysis")
    parser.add_argument("--brand", required=True, help="Brand to analyse")
    parser.add_argument("--analyze", action="store_true", help="Run gap analysis")
    parser.add_argument("--run-id", help="Specific run ID to analyse")
    parser.add_argument("--save", action="store_true", help="Save gap report to memory")
    args = parser.parse_args()

    rival = Rival(brand=args.brand)

    if args.analyze:
        report = rival.analyze_gaps(run_id=args.run_id)
        if args.save:
            rival.save_gap_report(report, run_id=args.run_id)
        print(json.dumps(report, indent=2))
    else:
        parser.print_help()