#!/usr/bin/env python3
"""
drift_detector.py — SENTINEL's daily drift detection engine
Compares AI mention rates for anchor prompts against 7-day rolling averages.
Flags statistically significant shifts in brand inclusion rates.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("sentinel.drift")

MEMORY_DIR = "/root/.openclaw/workspace/aisearch_system/memory"
ANCHOR_PROMPT_COUNT = 20
DRIFT_THRESHOLD_PCT = 15  # percentage points — flag if today's rate differs by >15pp from rolling avg

def load_response_log() -> list:
    """Load all entries from response_log.jsonl."""
    log_path = os.path.join(MEMORY_DIR, "response_log.jsonl")
    if not os.path.exists(log_path):
        return []
    entries = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries

def load_extractions() -> list:
    """Load all SIEVE extractions from sieve_output.jsonl."""
    path = os.path.join(MEMORY_DIR, "sieve_output.jsonl")
    if not os.path.exists(path):
        return []
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records

def get_anchor_prompt_ids() -> list:
    """Load the anchor prompt IDs (high_priority always-run set) from prompt_library.json."""
    lib_path = os.path.join(MEMORY_DIR, "prompt_library.json")
    with open(lib_path) as f:
        lib = json.load(f)
    return [p["id"] for p in lib.get("prompts", []) if p.get("priority") == "high"][:ANCHOR_PROMPT_COUNT]

def compute_daily_brand_rates(entries: list, brand: str, days: int = 7) -> dict:
    """
    Compute brand inclusion rate per day for the last `days` days.
    Returns dict: {date_string: {"total": N, "includes_brand": M, "rate": M/N}}
    """
    by_date = defaultdict(lambda: {"total": 0, "includes_brand": 0})
    cutoff = datetime.now() - timedelta(days=days)

    for entry in entries:
        try:
            captured_at = entry.get("captured_at", "")
            if not captured_at:
                continue
            dt = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
            if dt < cutoff:
                continue
        except Exception:
            continue

        by_date[date_str]["total"] += 1

        # Brand inclusion check — look in raw_response field
        raw_text = entry.get("raw_response", "") or ""
        if brand.lower() in raw_text.lower():
            by_date[date_str]["includes_brand"] += 1

    # Compute rates
    for date, counts in by_date.items():
        counts["rate"] = (counts["includes_brand"] / counts["total"]) if counts["total"] > 0 else 0.0

    return by_date

def compute_rolling_average(daily_rates: dict, days: int = 7) -> float:
    """Average the daily rates over the last `days` days."""
    rates = [v["rate"] for v in daily_rates.values() if v["total"] > 0]
    return sum(rates) / len(rates) if rates else 0.0

def detect_drift(brand: str) -> dict:
    """
    Detect whether today's brand inclusion rate for anchor prompts
    differs significantly from the 7-day rolling average.
    Returns a drift dict or None if insufficient data.
    """
    entries = load_response_log()
    if not entries:
        logger.info("No response log entries — insufficient data for drift detection")
        return None

    anchor_ids = get_anchor_prompt_ids()

    # Filter entries to anchor prompts only
    anchor_entries = [e for e in entries if e.get("prompt_id") in anchor_ids]

    today = datetime.now().strftime("%Y-%m-%d")
    cutoff_7d = datetime.now() - timedelta(days=7)

    today_entries = []
    historical_entries = []

    for entry in anchor_entries:
        try:
            captured_at = entry.get("captured_at", "")
            dt = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
        except Exception:
            continue
        if date_str == today:
            today_entries.append(entry)
        elif dt >= cutoff_7d:
            historical_entries.append(entry)

    if not today_entries:
        logger.info("No anchor prompt responses captured today yet")
        return None

    # Today's rate
    today_includes = sum(1 for e in today_entries if brand.lower() in (e.get("raw_response") or "").lower())
    today_rate = today_includes / len(today_entries) if today_entries else 0.0

    # Historical rate (last 7 days, excluding today)
    hist_includes = sum(1 for e in historical_entries if brand.lower() in (e.get("raw_response") or "").lower())
    hist_rate = hist_includes / len(hist_entries) if historical_entries else 0.0

    drift_pct = abs(today_rate - hist_rate) * 100

    drift_event = {
        "brand": brand,
        "date": today,
        "today_anchor_count": len(today_entries),
        "today_includes_brand": today_includes,
        "today_rate_pct": round(today_rate * 100, 2),
        "hist_rate_pct": round(hist_rate * 100, 2),
        "drift_pct": round(drift_pct, 2),
        "drift_detected": drift_pct > DRIFT_THRESHOLD_PCT,
        "direction": "POSITIVE" if today_rate > hist_rate else ("NEGATIVE" if today_rate < hist_rate else "STABLE"),
        "threshold_pct": DRIFT_THRESHOLD_PCT,
    }

    logger.info(f"Drift check: today={today_rate*100:.1f}% hist={hist_rate*100:.1f}% drift={drift_pct:.1f}pp "
                f"({drift_event['direction']})")
    return drift_event

def run_daily_drift_check(brands: list) -> list:
    """Run drift detection for all configured brands. Returns list of drift events."""
    events = []
    for brand in brands:
        event = detect_drift(brand)
        if event and event["drift_detected"]:
            events.append(event)
    return events

if __name__ == "__main__":
    import yaml
    config_path = "/root/.openclaw/workspace/aisearch_system/config/brands.yaml"
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = yaml.safe_load(f)
        brands = list(config.get("brands", {}).keys())
    else:
        brands = []

    events = run_daily_drift_check(brands)
    if events:
        print(f"⚠️  DRIFT DETECTED — {len(events)} event(s)")
        for e in events:
            print(f"  [{e['direction']}] {e['brand']}: today {e['today_rate_pct']}% vs hist {e['hist_rate_pct']}% "
                  f"(drift: {e['drift_pct']}pp)")
    else:
        print("✅ No drift detected.")
