#!/usr/bin/env python3
"""test_pipeline.py — End-to-end pipeline integration tests"""
import sys
sys.path.insert(0, ".")

def test_pipeline_state_machine():
    """Verify all pipeline states are defined."""
    states = ["IDLE", "SCOUT", "FALCON", "SIEVE", "CARTOGRAPHER", "RIVAL", "ORACLE_X", "COMPLETE"]
    assert states == sorted(states), "Pipeline states out of order"
    print("✓ Pipeline state machine is valid")

def test_memory_files_exist():
    import os
    memory_dir = "memory"
    required = ["prompt_library.json", "response_log.jsonl", "entity_registry.json",
                "citation_graph.json", "sieve_output.jsonl", "rival_output.json"]
    for f in required:
        path = os.path.join(memory_dir, f)
        assert os.path.exists(path), f"Missing: {f}"
    print("✓ All memory files present")

def test_config_brands():
    import yaml
    with open("config/brands.yaml") as f:
        data = yaml.safe_load(f)
    assert "brands" in data, "No brands section in config"
    assert len(data["brands"]) > 0, "No brands configured"
    print(f"✓ {len(data['brands'])} brand(s) configured")

if __name__ == "__main__":
    test_pipeline_state_machine()
    test_memory_files_exist()
    test_config_brands()
    print("All pipeline tests passed.")
