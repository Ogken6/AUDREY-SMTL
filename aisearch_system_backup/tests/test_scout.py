#!/usr/bin/env python3
"""test_scout.py — Tests for SCOUT prompt generation"""
import sys
sys.path.insert(0, ".")
from agents.scout import generate_queries

def test_query_generation():
    queries = generate_queries("crispyglaze.com", ["bbcgoodfood", "allrecipes"])
    assert len(queries) >= 50, f"Expected >=50 queries, got {len(queries)}"
    assert all("query_id" in q for q in queries), "Missing query_id in output"
    print(f"✓ Generated {len(queries)} queries")

def test_no_duplicate_categories():
    queries = generate_queries("crispyglaze.com", [])
    categories = [q["category"] for q in queries]
    assert len(categories) == len(set(categories)), "Duplicate category detected"
    print("✓ No duplicate categories")

if __name__ == "__main__":
    test_query_generation()
    test_no_duplicate_categories()
    print("All tests passed.")
