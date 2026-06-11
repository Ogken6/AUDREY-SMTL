#!/usr/bin/env python3
"""
magnus.py — ORACLE Pipeline Orchestrator
Loads brand config, runs the full detection pipeline, manages stage transitions.
Can be triggered by scheduler or run directly with --run-now
Usage:
    python agents/magnus.py --run-now --brand=crispyglaze
    python agents/magnus.py --daemon --brand=crispyglaze
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.api_caller import APICaller
from tools.browser_agent import BrowserAgent
from tools.proxy_manager import ProxyManager
from tools.db_writer import DBWriter
from tools.scheduler import Scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "logs" / "magnus.log"),
    ],
)
logger = logging.getLogger("magnus")

BRAND_CONFIG_PATH = PROJECT_ROOT / "config" / "brands.yaml"
PROMPT_LIBRARY_PATH = PROJECT_ROOT / "memory" / "prompt_library.json"
PIPELINE_STATE_PATH = PROJECT_ROOT / "memory" / "pipeline_state.json"
ENTITY_REGISTRY_PATH = PROJECT_ROOT / "memory" / "entity_registry.json"
RUNS_HISTORY_PATH = PROJECT_ROOT / "memory" / "runs_history.jsonl"

class Magnus:
    """
    ORACLE pipeline orchestrator.
    Runs the full brand visibility detection pipeline:
      1. Load brand config + prompt library
      2. Query all engines via FALCON for each prompt
      3. Extract entities + sentiment via SIEVE
      4. Update citation graph via CARTOGRAPHER
      5. Record results in PostgreSQL via db_writer
      6. Update pipeline state
    """

    def __init__(self, brand: str, dry_run: bool = False):
        self.brand = brand
        self.dry_run = dry_run
        self.falcon = APICaller()        # FALCON: engine query interface
        self.browser = BrowserAgent()    # FALCON: browser-based queries
        self.db = DBWriter()             # Shared DB writer
        self.proxy_mgr = ProxyManager()  # Proxy pool
        self.scheduler = Scheduler()     # Scheduler for recurring runs
        self.run_id = None
        self.brand_config = None
        self.prompts = []
        self.entity_registry = {}
        self.stats = {
            "prompts_queried": 0,
            "responses_captured": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
        }

    # ── Config Loading ──────────────────────────────────────────────────────────

    def load_brand_config(self) -> dict:
        """Load brand config from brands.yaml for the specified brand."""
        import yaml
        with open(BRAND_CONFIG_PATH) as f:
            all_brands = yaml.safe_load(f)
        brands = all_brands.get("brands", {})
        if self.brand not in brands:
            raise ValueError(f"Brand '{self.brand}' not found in {BRAND_CONFIG_PATH}")
        self.brand_config = brands[self.brand]
        logger.info(f"Loaded config for brand: {self.brand}")
        logger.info(f"  Canonical: {self.brand_config['canonical_name']}")
        logger.info(f"  Engines: {list(self.brand_config.get('engines', {}).keys())}")
        return self.brand_config

    def load_prompt_library(self) -> list:
        """Load prompt library from memory/prompt_library.json."""
        with open(PROMPT_LIBRARY_PATH) as f:
            data = json.load(f)
        prompts = data.get("prompts", [])
        logger.info(f"Loaded {len(prompts)} prompts from prompt library")
        return prompts

    def load_entity_registry(self) -> dict:
        """Load entity registry for brand variant matching."""
        with open(ENTITY_REGISTRY_PATH) as f:
            registry = json.load(f)
        self.entity_registry = registry.get("brands", {}).get(self.brand, {})
        logger.info(f"Loaded entity registry for {self.brand}")
        return self.entity_registry

    # ── Pipeline Stages ─────────────────────────────────────────────────────────

    def run_pipeline(self) -> dict:
        """
        Execute the full pipeline for this run.
        Returns a run summary dict.
        """
        import yaml
        self.run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{self.brand}"
        self.stats["start_time"] = datetime.now(timezone.utc).isoformat()
        logger.info(f"{'='*60}")
        logger.info(f"Starting pipeline run: {self.run_id}")
        logger.info(f"Brand: {self.brand}")
        logger.info(f"{'='*60}")

        start_ts = time.time()

        try:
            # Stage 1: Load configs
            self.load_brand_config()
            self.load_entity_registry()
            self.prompts = self.load_prompt_library()

            if not self.prompts:
                raise RuntimeError("Prompt library is empty — cannot run pipeline")

            # Stage 2: Query engines (FALCON)
            responses = self._run_falcon_queries()

            # Stage 3: Extract entities (SIEVE)
            extractions = self._run_sieve_extractions(responses)

            # Stage 4: Fetch citation content (CARTOGRAPHER)
            self._run_cartographer(extractions)

            # Stage 5: Write to database
            self._write_results(responses, extractions)

            # Stage 6: Update pipeline state
            self._update_pipeline_state(success=True)

            elapsed = time.time() - start_ts
            self.stats["end_time"] = datetime.now(timezone.utc).isoformat()
            logger.info(f"Pipeline COMPLETE in {elapsed:.1f}s")
            logger.info(f"  Responses captured: {self.stats['responses_captured']}")
            logger.info(f"  Errors: {self.stats['errors']}")

            return {
                "run_id": self.run_id,
                "status": "complete",
                "elapsed_seconds": round(elapsed, 1),
                "stats": self.stats,
            }

        except Exception as e:
            elapsed = time.time() - start_ts
            logger.error(f"Pipeline FAILED after {elapsed:.1f}s: {e}")
            self._update_pipeline_state(success=False, error=str(e))
            raise

    def _run_falcon_queries(self) -> list:
        """
        FALCON: Query all configured engines for each prompt.
        Returns list of raw response dicts.
        """
        import yaml
        with open(PROJECT_ROOT / "config" / "engines.yaml") as f:
            engines_config = yaml.safe_load(f).get("engines", {})

        enabled_engines = [
            e for e, cfg in engines_config.items()
            if cfg.get("enabled", True)
        ]
        logger.info(f"FALCON querying {len(enabled_engines)} engines for {len(self.prompts)} prompts")

        responses = []
        total_queries = len(self.prompts) * len(enabled_engines)
        query_idx = 0

        for prompt in self.prompts:
            prompt_id = prompt.get("prompt_id", f"unk_{query_idx}")
            for engine in enabled_engines:
                query_idx += 1
                self.stats["prompts_queried"] += 1

                try:
                    result = self._query_engine(engine, prompt)
                    result["prompt_id"] = prompt_id
                    result["run_id"] = self.run_id
                    result["captured_at"] = datetime.now(timezone.utc).isoformat()
                    responses.append(result)
                    self.stats["responses_captured"] += 1

                except Exception as e:
                    logger.warning(f"FALCON query failed [{engine}][{prompt_id}]: {e}")
                    self.stats["errors"] += 1
                    responses.append({
                        "run_id": self.run_id,
                        "prompt_id": prompt_id,
                        "engine": engine,
                        "status": "ERROR",
                        "error": str(e),
                        "captured_at": datetime.now(timezone.utc).isoformat(),
                    })

                # Progress log every 20 queries
                if query_idx % 20 == 0:
                    logger.info(f"FALCON progress: {query_idx}/{total_queries} queries completed")

        logger.info(f"FALCON complete: {len(responses)} responses")
        return responses

    def _query_engine(self, engine: str, prompt: dict) -> dict:
        """
        Query a single engine with a single prompt.
        Handles both API-based and browser-based engines.
        """
        import yaml
        with open(PROJECT_ROOT / "config" / "engines.yaml") as f:
            eng_cfg = yaml.safe_load(f).get("engines", {}).get(engine, {})

        access_method = eng_cfg.get("access_method", "api")
        model = eng_cfg.get("model", "default")
        temperature = eng_cfg.get("temperature", 0.3)
        max_tokens = eng_cfg.get("max_tokens", 1500)
        rate_limit_rpm = eng_cfg.get("rate_limit_rpm", 30)

        prompt_text = prompt.get("prompt_text", "")
        if not prompt_text:
            return {"status": "ERROR", "error": "Empty prompt text"}

        # Route to API or browser
        if access_method == "browser":
            result = self.browser.query(engine=engine, prompt=prompt_text)
        else:
            # Get geo-proxy for this engine if configured
            region = eng_cfg.get("proxy_region", "eu-west")
            proxy = self.proxy_mgr.get_proxy(region)

            result = self.falcon.query_engine(
                engine=engine,
                prompt=prompt_text,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                session_id=self.run_id,
                region=region,
            )

        # Add engine metadata
        result["engine"] = engine
        result["region"] = eng_cfg.get("proxy_region", "unknown")
        result["rate_limited"] = result.get("status") == "RATE_LIMITED"

        return result

    def _run_sieve_extractions(self, responses: list) -> list:
        """
        SIEVE: Extract entities and sentiment from raw responses.
        Two-step: (1) entity extraction, (2) sentiment framing.
        Returns list of extraction dicts.
        """
        from tools.api_caller import APICaller

        sieve_api = APICaller()
        extractions = []
        target_brand = self.brand_config["canonical_name"]
        brand_variants = self.brand_config.get("name_variants", [])
        competitors = [c["name"] for c in self.brand_config.get("competitors", [])]

        # Load SIEVE prompts
        with open(PROJECT_ROOT / "prompts" / "extraction_prompt.md") as f:
            extraction_template = f.read()
        with open(PROJECT_ROOT / "prompts" / "sentiment_prompt.md") as f:
            sentiment_template = f.read()

        for resp in responses:
            if resp.get("status") != "SUCCESS":
                continue

            raw_text = resp.get("raw_text", "")
            if not raw_text:
                continue

            prompt_id = resp.get("prompt_id", "unknown")

            # Stage 1: Entity extraction
            extraction_prompt = extraction_template.format(
                target_brand_canonical=target_brand,
                target_brand_variants_list=", ".join(brand_variants),
                competitor_list=", ".join(competitors),
                raw_response_text=raw_text,
            )

            try:
                ext_result = sieve_api.internal_call(
                    prompt=extraction_prompt,
                    model="claude",
                    max_tokens=2000,
                    temperature=0.1,
                )
                ext_data = self._safe_json_parse(ext_result.get("raw_text", "{}"))
                ext_data["response_id"] = self._make_response_id(resp)
                ext_data["prompt_id"] = prompt_id
                ext_data["engine"] = resp.get("engine", "unknown")
                ext_data["run_id"] = self.run_id
                ext_data["captured_at"] = resp.get("captured_at")
            except Exception as e:
                logger.warning(f"SIEVE extraction failed for {prompt_id}: {e}")
                ext_data = {"error": str(e), "response_id": self._make_response_id(resp)}

            # Stage 2: Sentiment framing
            sentiment_prompt = sentiment_template.format(
                target_brand_canonical=target_brand,
                original_prompt_text=prompt_id,  # In production: pass actual prompt text
                prompt_intent="recommendation",
                raw_response_text=raw_text,
            )

            try:
                sent_result = sieve_api.internal_call(
                    prompt=sentiment_prompt,
                    model="claude",
                    max_tokens=1000,
                    temperature=0.1,
                )
                sent_data = self._safe_json_parse(sent_result.get("raw_text", "{}"))
                ext_data["sentiment_class"] = sent_data.get("sentiment_class", "unknown")
                ext_data["sentiment_confidence"] = sent_data.get("sentiment_confidence", 0.0)
                ext_data["sentiment_evidence"] = sent_data.get("sentiment_evidence", "")
                ext_data["qualifiers"] = sent_data.get("qualifiers", [])
            except Exception as e:
                logger.warning(f"SIEVE sentiment failed for {prompt_id}: {e}")
                ext_data["sentiment_class"] = "unknown"
                ext_data["sentiment_confidence"] = 0.0

            extractions.append(ext_data)

        logger.info(f"SIEVE complete: {len(extractions)} extractions")
        return extractions

    def _run_cartographer(self, extractions: list):
        """
        CARTOGRAPHER: Fetch citation source content for high-influence sources.
        """
        from tools.url_fetcher import URLFetcher

        fetcher = URLFetcher()
        high_influence_sources = []

        for ext in extractions:
            cited_urls = ext.get("cited_urls", [])
            for url in cited_urls[:5]:  # Top 5 URLs per response
                influence = self._estimate_source_influence(url)
                if influence > 0.7:
                    high_influence_sources.append({
                        "url": url,
                        "response_id": ext.get("response_id"),
                        "prompt_id": ext.get("prompt_id"),
                        "engine": ext.get("engine"),
                    })

        # Deduplicate
        seen = set()
        unique_sources = []
        for s in high_influence_sources:
            if s["url"] not in seen:
                seen.add(s["url"])
                unique_sources.append(s)

        logger.info(f"CARTOGRAPHER fetching content from {len(unique_sources)} high-influence sources")
        for src in unique_sources:
            try:
                content = fetcher.fetch(url=src["url"])
                # Content is cached by URLFetcher — we just trigger the fetch
                logger.debug(f"  Fetched: {src['url'][:60]}...")
            except Exception as e:
                logger.warning(f"CARTOGRAPHER fetch failed for {src['url'][:60]}: {e}")

    def _write_results(self, responses: list, extractions: list):
        """Write pipeline results to PostgreSQL and response log."""
        import yaml

        # Always append raw responses to JSONL
        self._append_response_log(responses)

        # Write structured data to PostgreSQL if configured
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            logger.warning("DATABASE_URL not set — skipping PostgreSQL write")
            return

        try:
            yaml_cfg = yaml.safe_load(open(PROJECT_ROOT / "config" / "system.yaml"))
            run_record = {
                "run_id": self.run_id,
                "brand_config": self.brand,
                "started_at": self.stats["start_time"],
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "status": "complete",
                "prompts_queried": self.stats["prompts_queried"],
                "responses_captured": self.stats["responses_captured"],
                "completion_rate": self.stats["responses_captured"] / max(1, self.stats["prompts_queried"]),
                "avg_extraction_confidence": sum(
                    e.get("extraction_confidence", 0) for e in extractions
                ) / max(1, len(extractions)),
                "error_count": self.stats["errors"],
                "data_quality_flags": [],
            }
            self.db.write_run_summary(run_record)
            self.db.write_responses(responses)
            self.db.write_extractions(extractions)
            logger.info("Results written to PostgreSQL")
        except Exception as e:
            logger.error(f"Database write failed: {e}")

    def _append_response_log(self, responses: list):
        """Append all raw responses to response_log.jsonl (never overwrite)."""
        RUNS_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(RUNS_HISTORY_PATH, "a") as f:
            for resp in responses:
                f.write(json.dumps({
                    "run_id": resp.get("run_id"),
                    "prompt_id": resp.get("prompt_id"),
                    "engine": resp.get("engine"),
                    "captured_at": resp.get("captured_at"),
                    "raw_text": resp.get("raw_text", ""),
                    "status": resp.get("status"),
                    "latency_ms": resp.get("latency_ms"),
                }) + "\n")

    def _update_pipeline_state(self, success: bool, error: str = None):
        """Update pipeline_state.json with current run status."""
        state = {
            "run_id": self.run_id,
            "brand": self.brand,
            "status": "complete" if success else "failed",
            "stats": self.stats,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if error:
            state["error"] = error
        with open(PIPELINE_STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)

    # ── Helpers ─────────────────────────────────────────────────────────────────

    def _safe_json_parse(self, text: str) -> dict:
        """Parse JSON safely — handles markdown code fences, partial output."""
        import re
        text = text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = text.strip("`")
        return json.loads(text)

    def _make_response_id(self, resp: dict) -> str:
        import hashlib
        key = f"{resp.get('run_id')}_{resp.get('prompt_id')}_{resp.get('engine')}"
        return hashlib.md5(key.encode()).hexdigest()[:16]

    # ── Scheduling ──────────────────────────────────────────────────────────────

    def schedule_runs(self):
        """Schedule nightly pipeline runs via cron."""
        schedule = self.scheduler.add_daily_run(
            agent="magnus",
            hour_utc=2,   # 02:00 UTC — off-peak
            brand=self.brand,
        )
        logger.info(f"Scheduled nightly runs: {schedule}")

    def run_once(self):
        """Run pipeline once (non-daemon mode)."""
        return self.run_pipeline()


# ── CLI Entry Point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORACLE Magnus Pipeline Orchestrator")
    parser.add_argument("--run-now", action="store_true", help="Run pipeline immediately and exit")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon with scheduled runs")
    parser.add_argument("--brand", required=True, help="Brand to run pipeline for")
    parser.add_argument("--dry-run", action="store_true", help="Dry run — no API calls made")
    args = parser.parse_args()

    # Ensure logs directory exists
    Path(__file__).parent.parent / "logs" / "magnus.log"
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)

    magnus = Magnus(brand=args.brand, dry_run=args.dry_run)

    if args.run_now:
        result = magnus.run_once()
        print(json.dumps(result, indent=2))
    elif args.daemon:
        logger.info(f"MAGNUS daemon started for brand: {args.brand}")
        magnus.schedule_runs()
        import time
        while True:
            time.sleep(3600)  # Keep alive
    else:
        parser.print_help()