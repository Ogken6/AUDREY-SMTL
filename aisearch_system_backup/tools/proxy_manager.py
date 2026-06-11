#!/usr/bin/env python3
"""
proxy_manager.py — Rotating residential proxy management for FALCON
Manages proxy pools per region, supports sticky and rotating session types.
"""

import os
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)

REGIONS = ["us-east", "eu-west", "apac"]

class ProxyManager:
    """
    Manages a pool of rotating residential proxies for geographic diversity
    and IP-level rate limit avoidance.
    """

    def __init__(
        self,
        provider: str = "brightdata",
        api_key: Optional[str] = None,
        pool_size_per_region: int = 50,
    ):
        self.provider = provider
        self.api_key = api_key or os.environ.get("PROXY_API_KEY", "")
        self.pool_size = pool_size_per_region
        self._rotations = {r: 0 for r in REGIONS}
        self._blocked = set()

    def get_proxy(
        self,
        region: str = "eu-west",
        session_type: str = "rotating",
        protocol: str = "https",
    ) -> dict:
        """
        Get the next proxy for a region and session type.
        Returns a dict suitable for Playwright or requests proxy config.
        """
        try:
            import proxier  # Professional proxy provider library
            proxy_url = proxier.get_proxy(
                provider=self.provider,
                api_key=self.api_key,
                region=region,
                session_type=session_type,
            )
        except ImportError:
            # Fallback: construct proxy URL directly
            pool_pos = self._rotations[region] % self.pool_size
            self._rotations[region] += 1
            proxy_tag = f"{region}-{pool_pos + 1}"
            if not self.api_key:
                return {}  # No proxy available
            proxy_url = f"http://{proxy_tag}:{self.api_key}@proxy.example.com:8080"

        return {
            "http": proxy_url,
            "https": proxy_url,
            "region": region,
            "session_type": session_type,
            "provider": self.provider,
        }

    def health_check(self) -> dict:
        """
        Return proxy pool health status.
        Detects blocked IPs and reports availability per region.
        """
        try:
            import proxier
            status = proxier.pool_health(provider=self.provider, api_key=self.api_key)
            return status
        except ImportError:
            return {
                "pool_size": self.pool_size * len(REGIONS),
                "available": self.pool_size * len(REGIONS) - len(self._blocked),
                "blocked": len(self._blocked),
                "avg_latency_ms": None,
                "note": "Proxy health check unavailable — proxier library not installed",
            }

    def retire_proxy(self, proxy_id: str, reason: str = ""):
        """Flag a proxy IP as blocked/unusable."""
        self._blocked.add(proxy_id)
        logger.warning(f"Proxy retired: {proxy_id} — reason: {reason}")

    def reset_rotation(self, region: Optional[str] = None):
        """Reset rotation counter for a region (or all regions)."""
        if region:
            self._rotations[region] = 0
        else:
            for r in REGIONS:
                self._rotations[r] = 0

    def best_for(self, brand_region: str = "UK") -> dict:
        """Return the optimal proxy for a brand's home market."""
        region_map = {"UK": "eu-west", "IE": "eu-west", "EU": "eu-west",
                      "US": "us-east", "APAC": "apac"}
        return self.get_proxy(region=region_map.get(brand_region, "eu-west"))
