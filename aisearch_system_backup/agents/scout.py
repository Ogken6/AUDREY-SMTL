#!/usr/bin/env python3
"""
scout.py — ORACLE Prompt Generation Agent
Generates, refines, and manages the brand-specific prompt library.
Builds prompts that real users would type into AI search engines.
Usage:
    python agents/scout.py --brand=crispyglaze --initial-build
    python agents/scout.py --brand=crispyglaze --generate --count=30
    python agents/scout.py --brand=crispyglaze --dedup-only
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
logger = logging.getLogger("scout")

PROMPT_LIBRARY_PATH = PROJECT_ROOT / "memory" / "prompt_library.json"
BRAND_CONFIG_PATH = PROJECT_ROOT / "config" / "brands.yaml"
SCOUT_TEMPLATE_PATH = PROJECT_ROOT / "prompts" / "scout_generation.md"

INTENT_DISTRIBUTION = {
    "recommendation": 0.30,
    "comparison": 0.20,
    "problem_framing": 0.20,
    "tool_discovery": 0.15,
    "validation": 0.10,
    "alternatives": 0.05,
}

class Scout:
    """
    SCOUT generates and manages the prompt library.
    SCOUT is invoked by MAGNUS before pipeline runs to ensure the prompt
    library is fresh and comprehensive for the target brand.
    """

    def __init__(self, brand: str):
        self.brand = brand
        self.api = APICaller()
        self.brand_config = self._load_brand_config()
        self.prompt_library = self._load_prompt_library()

    def _load_brand_config(self) -> dict:
        import yaml
        with open(BRAND_CONFIG_PATH) as f:
            all_brands = yaml.safe_load(f).get("brands", {})
        if self.brand not in all_brands:
            raise ValueError(f"Brand '{self.brand}' not found in brands.yaml")
        return all_brands[self.brand]

    def _load_prompt_library(self) -> dict:
        if PROMPT_LIBRARY_PATH.exists():
            with open(PROMPT_LIBRARY_PATH) as f:
                return json.load(f)
        return {"prompts": [], "metadata": {"brand": self.brand, "last_updated": None}}

    def _save_prompt_library(self):
        self.prompt_library["metadata"] = {
            "brand": self.brand,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_prompts": len(self.prompt_library["prompts"]),
        }
        PROMPT_LIBRARY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PROMPT_LIBRARY_PATH, "w") as f:
            json.dump(self.prompt_library, f, indent=2)
        logger.info(f"Saved prompt library: {len(self.prompt_library['prompts'])} prompts")

    def generate_prompts(self, count: int = 50) -> list:
        """
        Generate 'count' new prompts using LLM generation.
        Returns list of prompt dicts.
        """
        with open(SCOUT_TEMPLATE_PATH) as f:
            template = f.read()

        category = self.brand_config.get("category", "general")
        personas = self.brand_config.get("target_personas", [])
        competitors = [c["name"] for c in self.brand_config.get("competitors", [])]
        competitor_str = ", ".join(competitors) if competitors else "None specified"

        dist_parts = [f"{k}: {v*100:.0f}%" for k, v in INTENT_DISTRIBUTION.items()]
        dist_str = ", ".join(dist_parts)

        prompt = template.format(
            category=category,
            personas=", ".join(personas),
            competitors=competitor_str,
            intent_types_needed="recommendation, comparison, problem_framing, tool_discovery, validation, alternatives",
            count=count,
            intent_distribution=dist_str,
        )

        logger.info(f"Generating {count} prompts for brand: {self.brand}")

        try:
            result = self.api.internal_call(
                prompt=prompt,
                model="claude",
                max_tokens=4000,
                temperature=0.8,
            )
            raw_text = result.get("raw_text", "")

            # Parse JSON array from response
            import re
            json_match = re.search(r'\[[\s\S]*\]', raw_text)
            if json_match:
                new_prompts = json.loads(json_match.group())
            else:
                logger.warning("Could not parse prompt JSON from LLM response")
                new_prompts = []

            # Enrich with metadata
            for i, p in enumerate(new_prompts):
                p["prompt_id"] = f"{self.brand[:3].upper()}_{datetime.now().strftime('%m%d')}_{i:03d}"
                p["brand"] = self.brand
                p["source"] = "scout_generation"
                p["added_at"] = datetime.now(timezone.utc).isoformat()
                p["run_count"] = 0
                p["verified_real"] = False
                p["anchor"] = False

            logger.info(f"Generated {len(new_prompts)} prompts")
            return new_prompts

        except Exception as e:
            logger.error(f"Prompt generation failed: {e}")
            return []

    def add_prompts(self, new_prompts: list):
        """Add new prompts to the library, avoiding exact duplicates."""
        existing = {p["text"] for p in self.prompt_library["prompts"]}
        added = 0
        for p in new_prompts:
            if p["text"] not in existing:
                self.prompt_library["prompts"].append(p)
                added += 1
        logger.info(f"Added {added} new prompts (skipped {len(new_prompts) - added} duplicates)")
        self._save_prompt_library()
        return added

    def deduplicate(self, threshold: float = 0.92) -> int:
        """
        Remove near-duplicate prompts using semantic similarity.
        Uses the LLM to score pairwise similarity.
        """
        from tools.api_caller import APICaller
        api = APICaller()

        prompts = self.prompt_library["prompts"]
        if len(prompts) < 2:
            return 0

        logger.info(f"Deduping {len(prompts)} prompts (threshold={threshold})")
        kept = [prompts[0]]  # Always keep first prompt
        removed = 0

        for candidate in prompts[1:]:
            is_duplicate = False
            for existing in kept:
                try:
                    similarity_prompt = (
                        f"Rate similarity of these two search prompts on a scale of 0.0 to 1.0 "
                        f"(1.0 = identical meaning, 0.0 = completely different):\n\n"
                        f"Prompt A: {existing['text']}\n"
                        f"Prompt B: {candidate['text']}\n\n"
                        f"Respond with only a number between 0.0 and 1.0."
                    )
                    result = api.internal_call(similarity_prompt, model="claude",
                                                max_tokens=50, temperature=0.0)
                    score = float(result.get("raw_text", "0").strip())
                    if score >= threshold:
                        is_duplicate = True
                        break
                except Exception:
                    continue

            if not is_duplicate:
                kept.append(candidate)
            else:
                removed += 1

        self.prompt_library["prompts"] = kept
        self._save_prompt_library()
        logger.info(f"Deduplication complete: removed {removed}, kept {len(kept)}")
        return removed

    def set_anchor_prompts(self, prompt_ids: list):
        """Mark specified prompts as anchor prompts (always included in runs)."""
        for p in self.prompt_library["prompts"]:
            p["anchor"] = p.get("prompt_id") in prompt_ids
        self._save_prompt_library()
        logger.info(f"Set {len(prompt_ids)} anchor prompts")

    def retire_prompts(self, prompt_ids: list, reason: str = ""):
        """Retire prompts from the active library (never deleted, marked retired)."""
        for p in self.prompt_library["prompts"]:
            if p.get("prompt_id") in prompt_ids:
                p["retired_at"] = datetime.now(timezone.utc).isoformat()
                p["retirement_reason"] = reason
        self._save_prompt_library()
        logger.info(f"Retired {len(prompt_ids)} prompts")

    def generate_initial_library(self, target_count: int = 80) -> int:
        """Build an initial prompt library from scratch."""
        logger.info(f"Building initial prompt library for {self.brand} (target: {target_count})")
        new_prompts = self.generate_prompts(count=target_count)
        self.add_prompts(new_prompts)
        self.deduplicate()
        return len(self.prompt_library["prompts"])


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORACLE SCOUT — Prompt Generation")
    parser.add_argument("--brand", required=True, help="Brand name")
    parser.add_argument("--initial-build", action="store_true",
                        help="Build initial prompt library from scratch")
    parser.add_argument("--generate", action="store_true",
                        help="Generate new prompts and add to library")
    parser.add_argument("--count", type=int, default=50,
                        help="Number of prompts to generate")
    parser.add_argument("--dedup-only", action="store_true",
                        help="Run deduplication only")
    parser.add_argument("--set-anchor", nargs="+", help="Set anchor prompts by ID")
    parser.add_argument("--retire", nargs="+", help="Retire prompts by ID")
    parser.add_argument("--list", action="store_true", help="List current prompts")
    args = parser.parse_args()

    scout = Scout(brand=args.brand)

    if args.initial_build:
        count = scout.generate_initial_library(target_count=args.count)
        print(f"Initial library built: {count} prompts")

    elif args.generate:
        new = scout.generate_prompts(count=args.count)
        added = scout.add_prompts(new)
        print(f"Generated {len(new)} prompts, added {added} new to library")

    elif args.dedup_only:
        removed = scout.deduplicate()
        print(f"Deduplication complete: removed {removed} duplicates")

    elif args.set_anchor:
        scout.set_anchor_prompts(args.set_anchor)
        print(f"Set {len(args.set_anchor)} anchor prompts")

    elif args.retire:
        scout.retire_prompts(args.retire, reason="manual_retire")
        print(f"Retired {len(args.retire)} prompts")

    elif args.list:
        for p in scout.prompt_library["prompts"]:
            anchor_tag = " [ANCHOR]" if p.get("anchor") else ""
            retired_tag = " [RETIRED]" if p.get("retired_at") else ""
            print(f"  {p['prompt_id']}{anchor_tag}{retired_tag} — {p['text'][:70]}")

    else:
        parser.print_help()