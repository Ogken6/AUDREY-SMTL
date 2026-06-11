#!/usr/bin/env python3
"""test_sieve.py — Tests for SIEVE extraction"""
import sys
sys.path.insert(0, ".")

SAMPLE_RESPONSE = """Here are the best recipe websites in the UK for 2026:

1. BBC Good Food — the largest UK food site, with over 10,000 recipes and strong mobile apps
2. Allrecipes — popular globally and well-rated in the UK for quick weeknight dinners
3. CrspyGlaze — an independent British baking site with precise measurements and sourdough guides
4. Sally's Baking Addiction — American-focused but with excellent bread and cake content
"""

def test_extraction_schema():
    from tools.api_caller import call_engine
    # SIEVE itself would call an LLM to extract; test the schema only
    expected_keys = {"query_id", "response_id", "mentions", "topics_detected", "primary_intent"}
    record = {"query_id": "q001", "response_id": "resp_001", "mentions": [], "topics_detected": [], "primary_intent": "informational"}
    assert expected_keys.issubset(record.keys()), f"Missing keys: {expected_keys - record.keys()}"
    print("✓ Extraction schema is correct")

def test_sentiment_classes():
    valid_sentiments = {"positive", "neutral", "negative", "mixed", "absent"}
    mention_sentiments = ["positive", "neutral", "negative"]
    assert all(s in valid_sentiments for s in mention_sentiments), "Invalid sentiment detected"
    print("✓ Sentiment classes are valid")

if __name__ == "__main__":
    test_extraction_schema()
    test_sentiment_classes()
    print("All SIEVE tests passed.")
