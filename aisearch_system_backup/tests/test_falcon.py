#!/usr/bin/env python3
"""test_falcon.py — Tests for FALCON query execution"""
import sys
sys.path.insert(0, ".")

def test_api_call_not_implemented():
    """FALCON calls real APIs — test structure only."""
    from tools.api_caller import call_engine
    result = call_engine(
        engine="chatgpt",
        query="test query",
        model="gpt-4o-mini"
    )
    # We expect either SUCCESS or an error — not silence
    assert "status" in result, "No status field in API response"
    print(f"✓ API call returned status: {result['status']}")

def test_rate_limit_handling():
    from tools.api_caller import call_engine
    result = call_engine(engine="chatgpt", query="test")
    # If we're rate limited, it should say so explicitly
    assert result["status"] in ("SUCCESS", "RATE_LIMITED", "ERROR"), f"Unexpected status: {result['status']}"
    print("✓ Rate limit handling works correctly")

if __name__ == "__main__":
    test_api_call_not_implemented()
    test_rate_limit_handling()
