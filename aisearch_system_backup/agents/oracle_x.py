#!/usr/bin/env python3
"""
oracle_x.py — ORACLE Recommendation Engine
Consumes gap analysis from RIVAL, citation graph from CARTOGRAPHER,
and generates prioritised, actionable recommendations.
MAX 5 P1 RECOMMENDATIONS per report — more is a failure to prioritise.
Usage:
    python agents/oracle_x.py --generate --brand=crispyglaze --run-id=run_20260527
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.api_caller import APICaller

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger("oracle_x")

REC_TEMPLATE_PATH = PROJECT_ROOT / "prompts" / "recommendation_prompt.md"
GAP_REPORTS_PATH = PROJECT_ROOT / "memory" / "competitive_reports"
CITATION_GRAPH_PATH = PROJECT_ROOT / "memory" / "citation_graph.json"
OUTPUT_PATH = PROJECT_ROOT / "memory" / "oracle_x_recommendations.json"

class OracleX:
    """
    ORACLE-X is the recommendation engine.
    It reads RIVAL gap reports and CARTOGRAPHER citation data,
    and generates specific, prioritised, actionable recommendations.

    Strict rules:
    - Maximum 5 P1 recommendations per report
    - Every recommendation must cite the specific gap it addresses
    - Recommendations must be AI-search native (not traditional SEO)
    - Effort estimates must be realistic (no "quick wins" requiring 6 months)
    """

    def __init__(self, brand: str):
        self.brand = brand
        self.api = APICaller()
        self.brand_config = self._load_brand_config()
        self.rec_template = self._load_template(REC_TEMPLATE_PATH)
        self.citation_graph = self._load_citation_graph()

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

    def _load_citation_graph(self) -> dict:
        if CITATION_GRAPH_PATH.exists():
            with open(CITATION_GRAPH_PATH) as f:
                return json.load(f)
        return {"nodes": {}, "edges": []}

    def _load_gap_report(self, run_id: str = None) -> dict:
        if not GAP_REPORTS_PATH.exists():
            return {}
        files = sorted(GAP_REPORTS_PATH.glob("gap_report_*.json"), reverse=True)
        if not files:
            return {}
        target_file = GAP_REPORTS_PATH / f"gap_report_{run_id}.json" if run_id else files[0]
        if not target_file.exists():
            target_file = files[0]
        with open(target_file) as f:
            return json.load(f)

    # ── Recommendation Generation ─────────────────────────────────────────────

    def generate(self, run_id: str = None) -> dict:
        """
        Main entry point: generate ORACLE-X recommendations.
        Returns full recommendation report.
        """
        logger.info(f"ORACLE-X generating recommendations for brand: {self.brand}")

        gap_report = self._load_gap_report(run_id)
        if not gap_report:
            logger.warning("No gap report found — cannot generate recommendations")
            return {"recommendations": [], "status": "no_data"}

        gaps = gap_report.get("gaps", [])
        displacement_events = gap_report.get("displacement_events", [])

        # Calculate current metrics
        inclusion_rate = self._calc_inclusion_rate(gap_report)
        wow_change = 0.0  # Would need previous period for real WoW
        high_severity_count = sum(1 for g in gaps if g.get("gap_severity") == "high")

        # Build citation highlights (top 20 sources)
        citation_highlights = self._citation_highlights()

        # Build gap map JSON
        gap_map_json = json.dumps(gaps[:50], indent=2)  # Cap at 50 for token limit

        prompt = self.rec_template.format(
            target_brand=self.brand_config["canonical_name"],
            report_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            gap_map_json=gap_map_json,
            citation_graph_highlights_json=json.dumps(citation_highlights, indent=2),
            displacement_events_json=json.dumps(displacement_events[:20], indent=2),
            inclusion_rate=round(inclusion_rate * 100, 1),
            wow_change=round(wow_change * 100, 1),
            high_severity_gap_count=high_severity_count,
        )

        try:
            result = self.api.internal_call(
                prompt=prompt,
                model="claude",
                max_tokens=4000,
                temperature=0.3,
            )
            raw = result.get("raw_text", "{}")
            import re
            json_match = re.search(r'\{[\s\S]*\}', raw)
            if json_match:
                report = json.loads(json_match.group())
            else:
                report = json.loads(raw)
        except Exception as e:
            logger.error(f"ORACLE-X LLM generation failed: {e}")
            report = {"recommendations": [], "status": "error", "error": str(e)}

        report["brand"] = self.brand
        report["run_id"] = run_id or "latest"
        report["generated_at"] = datetime.now(timezone.utc).isoformat()
        report["status"] = "success"

        # Enforce P1 cap
        p1_recs = [r for r in report.get("recommendations", []) if r.get("priority") == 1]
        if len(p1_recs) > 5:
            logger.error(f"ORACLE-X P1 CAP VIOLATION: {len(p1_recs)} P1 recommendations generated (max 5)")
            # Keep only top 5 by effort (prefer low effort)
            p1_recs.sort(key=lambda r: {"low": 0, "medium": 1, "high": 2}.get(r.get("effort", "high"), 2))
            report["recommendations"] = p1_recs[:5] + [
                r for r in report["recommendations"] if r.get("priority") != 1
            ]

        # Save report
        self._save_report(report)

        p1_count = sum(1 for r in report.get("recommendations", []) if r.get("priority") == 1)
        logger.info(f"ORACLE-X complete: {len(report['recommendations'])} recommendations ({p1_count} P1)")

        return report

    # ── Supporting Calculations ──────────────────────────────────────────────

    def _calc_inclusion_rate(self, gap_report: dict) -> float:
        """Calculate brand inclusion rate from gap report."""
        # If brand is absent in a prompt + competitor is present = gap
        # Inclusion rate = 1 - (brand_absent_gaps / total_prompts)
        # Simple heuristic using gap data
        gaps = gap_report.get("gaps", [])
        if not gaps:
            return 1.0
        brand_absent = sum(1 for g in gaps if g.get("gap_type") == "brand_absent")
        total = len(set(g.get("prompt_id") for g in gaps))
        if total == 0:
            return 1.0
        return 1.0 - (brand_absent / total)

    def _citation_highlights(self, top_n: int = 20) -> list:
        """Get top N most-cited sources from citation graph."""
        nodes = self.citation_graph.get("nodes", {})
        if not nodes:
            return []
        sorted_nodes = sorted(
            [{"url": url, **node} for url, node in nodes.items()],
            key=lambda x: x.get("citation_count", 0),
            reverse=True,
        )[:top_n]
        return [
            {
                "url": n["url"],
                "influence_score": n.get("influence_score", 0),
                "citation_count": n.get("citation_count", 0),
                "source_type": n.get("source_type", "unknown"),
                "engines_citing": n.get("engines_citing", []),
            }
            for n in sorted_nodes
        ]

    def _save_report(self, report: dict):
        """Save recommendation report to memory."""
        with open(OUTPUT_PATH, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Saved ORACLE-X report to {OUTPUT_PATH}")

    # ── Recommendation Filtering ──────────────────────────────────────────────

    def get_p1_actions(self) -> list:
        """Return current P1 actions for the action board."""
        if not OUTPUT_PATH.exists():
            return []
        with open(OUTPUT_PATH) as f:
            report = json.load(f)
        return [r for r in report.get("recommendations", []) if r.get("priority") == 1]

    def get_actions_by_type(self, rec_type: str) -> list:
        """Return all recommendations of a specific type."""
        if not OUTPUT_PATH.exists():
            return []
        with open(OUTPUT_PATH) as f:
            report = json.load(f)
        return [r for r in report.get("recommendations", []) if r.get("type") == rec_type]


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORACLE ORACLE-X — Recommendation Engine")
    parser.add_argument("--brand", required=True, help="Brand to generate recommendations for")
    parser.add_argument("--generate", action="store_true", help="Generate new recommendations")
    parser.add_argument("--run-id", help="Run ID to base recommendations on")
    parser.add_argument("--p1-only", action="store_true", help="Show only P1 recommendations")
    parser.add_argument("--by-type", help="Filter by recommendation type")
    args = parser.parse_args()

    oracle_x = OracleX(brand=args.brand)

    if args.generate:
        report = oracle_x.generate(run_id=args.run_id)
        print(json.dumps(report, indent=2))
    elif args.p1_only:
        actions = oracle_x.get_p1_actions()
        for a in actions:
            print(f"[P1] {a.get('rec_id')} — {a.get('action', 'N/A')[:80]}")
    elif args.by_type:
        actions = oracle_x.get_actions_by_type(args.by_type)
        print(json.dumps(actions, indent=2))
    else:
        parser.print_help()