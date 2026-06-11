#!/usr/bin/env python3
"""
sieve.py — ORACLE Entity Extraction & Sentiment Agent
Two-stage extraction pipeline:
  Stage 1: Extract all brand/entity mentions from raw AI responses
  Stage 2: Classify sentiment framing for the target brand
Both stages use LLM calls — never combined into one call (per ORACLE spec).
Usage:
    python agents/sieve.py --process-run --run-id=run_20260527_crispyglaze
"""

import os
import sys
import json
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.api_caller import APICaller
from tools.db_writer import DBWriter

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger("sieve")

RESPONSE_LOG_PATH = PROJECT_ROOT / "memory" / "response_log.jsonl"
EXTRACTIONS_OUT_PATH = PROJECT_ROOT / "memory" / "extractions"

EXTRACTION_TEMPLATE_PATH = PROJECT_ROOT / "prompts" / "extraction_prompt.md"
SENTIMENT_TEMPLATE_PATH = PROJECT_ROOT / "prompts" / "sentiment_prompt.md"

class Sieve:
    """
    SIEVE extracts structured data from raw AI responses.
    Stage 1: Entity extraction (brand mentions, competitor positions, citation URLs)
    Stage 2: Sentiment framing (how the target brand is positioned in the response)
    Two separate LLM calls — never combined.
    """

    def __init__(self, brand: str):
        self.brand = brand
        self.api = APICaller()
        self.db = DBWriter()
        self.brand_config = self._load_brand_config()
        self.extraction_template = self._load_template(EXTRACTION_TEMPLATE_PATH)
        self.sentiment_template = self._load_template(SENTIMENT_TEMPLATE_PATH)

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

    def _load_response_log(self, run_id: str = None) -> list:
        """Load responses from response_log.jsonl, optionally filtered by run_id."""
        responses = []
        if not RESPONSE_LOG_PATH.exists():
            return responses
        with open(RESPONSE_LOG_PATH) as f:
            for line in f:
                try:
                    resp = json.loads(line)
                    if run_id and resp.get("run_id") != run_id:
                        continue
                    if resp.get("status") == "SUCCESS" and resp.get("raw_text"):
                        responses.append(resp)
                except json.JSONDecodeError:
                    continue
        return responses

    # ── Stage 1: Entity Extraction ────────────────────────────────────────────

    def extract_entities(self, raw_text: str) -> dict:
        """
        Stage 1: Extract all brand/entity mentions from a raw AI response.
        Returns structured extraction dict.
        """
        target_brand = self.brand_config["canonical_name"]
        variants = self.brand_config.get("name_variants", [])
        competitors = [c["name"] for c in self.brand_config.get("competitors", [])]

        prompt = self.extraction_template.format(
            target_brand_canonical=target_brand,
            target_brand_variants_list=", ".join(variants),
            competitor_list=", ".join(competitors),
            raw_response_text=raw_text[:8000],  # Truncate to avoid token overflow
        )

        try:
            result = self.api.internal_call(
                prompt=prompt,
                model="claude",
                max_tokens=2000,
                temperature=0.1,
            )
            raw_out = result.get("raw_text", "{}")
            data = self._parse_json(raw_out)
            data["extraction_status"] = "success"
            return data
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
            return {"extraction_status": "error", "error": str(e), "entities": []}

    # ── Stage 2: Sentiment Framing ─────────────────────────────────────────────

    def classify_sentiment(self, raw_text: str, prompt_text: str = "") -> dict:
        """
        Stage 2: Classify how the target brand is framed in the response.
        Always a separate LLM call from entity extraction.
        """
        target_brand = self.brand_config["canonical_name"]

        prompt = self.sentiment_template.format(
            target_brand_canonical=target_brand,
            original_prompt_text=prompt_text or "general search query",
            prompt_intent="recommendation",
            raw_response_text=raw_text[:8000],
        )

        try:
            result = self.api.internal_call(
                prompt=prompt,
                model="claude",
                max_tokens=1000,
                temperature=0.1,
            )
            raw_out = result.get("raw_text", "{}")
            data = self._parse_json(raw_out)
            data["sentiment_status"] = "success"
            return data
        except Exception as e:
            logger.warning(f"Sentiment classification failed: {e}")
            return {"sentiment_status": "error", "error": str(e), "sentiment_class": "unknown"}

    # ── Combined Pipeline ─────────────────────────────────────────────────────

    def process_response(self, resp: dict) -> dict:
        """
        Process a single response through both SIEVE stages.
        Returns combined extraction + sentiment dict.
        """
        raw_text = resp.get("raw_text", "")
        prompt_text = resp.get("prompt", "")
        prompt_id = resp.get("prompt_id", "unknown")
        engine = resp.get("engine", "unknown")

        # Stage 1: Entity extraction
        extraction = self.extract_entities(raw_text)

        # Stage 2: Sentiment framing
        sentiment = self.classify_sentiment(raw_text, prompt_text)

        # Combine
        combined = {
            "response_id": self._make_response_id(resp),
            "run_id": resp.get("run_id"),
            "prompt_id": prompt_id,
            "engine": engine,
            "captured_at": resp.get("captured_at"),
            # From entity extraction
            "brand_present": extraction.get("brand_present"),
            "brand_position_rank": extraction.get("brand_position_rank"),
            "brand_recommendation_position": extraction.get("brand_recommendation_position"),
            "cited_urls": extraction.get("cited_urls", []),
            "entities": extraction.get("entities", []),
            "competitor_count_in_response": extraction.get("competitor_count_in_response", 0),
            "competitors_ranked_above_brand": extraction.get("competitors_ranked_above_brand", []),
            "extraction_confidence": extraction.get("extraction_confidence", 0.0),
            "extraction_confidence_reason": extraction.get("extraction_confidence_reason", ""),
            # From sentiment
            "sentiment_class": sentiment.get("sentiment_class", "unknown"),
            "sentiment_confidence": sentiment.get("sentiment_confidence", 0.0),
            "sentiment_evidence": sentiment.get("sentiment_evidence", ""),
            "qualifiers": sentiment.get("qualifiers", []),
            "framing_notes": sentiment.get("framing_notes"),
            # Status
            "processing_status": "complete",
        }

        return combined

    def process_run(self, run_id: str = None) -> list:
        """
        Process all responses in the response log for a given run.
        Returns list of extraction dicts.
        """
        logger.info(f"SIEVE processing{' run_id=' + run_id if run_id else ''}")
        responses = self._load_response_log(run_id)
        logger.info(f"Loaded {len(responses)} responses to process")

        extractions = []
        for resp in responses:
            try:
                ext = self.process_response(resp)
                extractions.append(ext)
            except Exception as e:
                logger.warning(f"SIEVE failed for response {resp.get('response_id')}: {e}")
                extractions.append({
                    "response_id": self._make_response_id(resp),
                    "run_id": resp.get("run_id"),
                    "prompt_id": resp.get("prompt_id"),
                    "engine": resp.get("engine"),
                    "processing_status": "error",
                    "error": str(e),
                })

        # Save extractions to file
        EXTRACTIONS_OUT_PATH.mkdir(parents=True, exist_ok=True)
        out_file = EXTRACTIONS_OUT_PATH / f"extractions_{run_id or 'latest'}.json"
        with open(out_file, "w") as f:
            json.dump(extractions, f, indent=2)

        # Write to DB if available
        self._write_to_db(extractions)

        success_count = sum(1 for e in extractions if e.get("processing_status") == "complete")
        logger.info(f"SIEVE complete: {success_count}/{len(extractions)} successful extractions")
        return extractions

    def _write_to_db(self, extractions: list):
        """Write extraction records to PostgreSQL."""
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            return
        try:
            self.db.write_extractions(extractions)
            logger.info(f"Wrote {len(extractions)} extractions to database")
        except Exception as e:
            logger.error(f"Failed to write extractions to DB: {e}")

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _parse_json(self, text: str) -> dict:
        """Parse JSON from LLM output — handles markdown fences, partial output."""
        text = text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = text.strip("`")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON block
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return {}

    def _make_response_id(self, resp: dict) -> str:
        import hashlib
        key = f"{resp.get('run_id')}_{resp.get('prompt_id')}_{resp.get('engine')}"
        return hashlib.md5(key.encode()).hexdigest()[:16]


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORACLE SIEVE — Entity Extraction & Sentiment")
    parser.add_argument("--brand", required=True, help="Brand to process")
    parser.add_argument("--process-run", action="store_true", help="Process all responses for a run")
    parser.add_argument("--run-id", help="Run ID to process")
    parser.add_argument("--test", help="Test extraction on a single text")
    args = parser.parse_args()

    sieve = Sieve(brand=args.brand)

    if args.test:
        result = sieve.extract_entities(args.test)
        print(json.dumps(result, indent=2))
    elif args.process_run:
        extractions = sieve.process_run(run_id=args.run_id)
        print(f"Processed {len(extractions)} extractions")
    else:
        parser.print_help()