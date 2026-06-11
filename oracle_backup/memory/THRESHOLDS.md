# THRESHOLDS.md — Alert and Quality Thresholds

**File:** `aisearch_system/config/thresholds.yaml`

## Quality Gates

| Gate | Threshold | Effect When Breached |
|---|---|---|
| FALCON min completion rate | ≥ 80% | Pipeline continues but run flagged degraded |
| FALCON max personalisation rate | ≤ 2% | Flag and rotate sessions; skip if sustained |
| SIEVE min extraction confidence | ≥ 0.65 | Individual record flagged for human review |
| SIEVE avg confidence threshold | ≥ 0.75 | Pipeline gate — run flagged degraded below this |
| CARTOGRAPHER min URL coverage | ≥ 60% | RIVAL notified to weight analysis accordingly |

## Drift Detection
- **Drift threshold:** ±15 percentage points on anchor prompts vs 7-day rolling average
- **High severity drift:** ±25 percentage points
- **Lookback:** 7 days

## Storage Alerts
| Check | Threshold | Severity |
|---|---|---|
| Disk usage | > 70% | WARNING |
| Disk usage | > 85% | ERROR — trigger archive job |
| Disk usage | > 95% | CRITICAL |
| Backup age | > 25 hours | ERROR |

## Agent Liveness Alerts
| Agent | Alert If Silent For |
|---|---|
| MAGNUS | > 26 hours |
| SCOUT | > 8 days |
| FALCON | > 26 hours |
| SIEVE | > 28 hours |
| CARTOGRAPHER | > 8 hours |
| RIVAL | > 26 hours |
| ORACLE-X | > 8 days |

## Proxy Pool Alerts
| Available IPs | Severity |
|---|---|
| < 30 per region | WARNING |
| < 10 per region | CRITICAL — FALCON cannot run |

## Competitive Alerts
| Trigger | Threshold | Severity |
|---|---|---|
| SoV decline | > 5 points | WARNING |
| SoV decline | > 10 points | ERROR |
| New high-severity gaps per week | > 5 | WARNING |
| Displacement events | > 3 | Immediate alert |