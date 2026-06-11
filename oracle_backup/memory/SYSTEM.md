# SYSTEM.md — ORACLE Master Configuration

**File:** `aisearch_system/config/system.yaml`

## System Identity
```yaml
system:
  name: "ORACLE"
  version: "1.0.0"
  environment: "production"
  timezone: "UTC"
  log_level: "INFO"
  log_dir: "logs/"
  data_dir: "memory/"
  snapshot_dir: "memory/snapshots/"
```

## Storage Paths
| Path | Purpose |
|---|---|
| `memory/response_log.jsonl` | Append-only raw AI responses |
| `memory/prompt_library.json` | Live prompt library |
| `memory/citation_graph.json` | Citation relationships |
| `memory/entity_registry.json` | Brands and competitors |
| `memory/pipeline_state.json` | Live pipeline state |
| `memory/snapshots/` | Daily archives (90-day retention) |

Max response log size: **50 GB** before archive trigger.

## Pipeline Schedule
| Job | Cron | Description |
|---|---|---|
| Full pipeline run | `0 2 * * *` | Daily 02:00 UTC |
| Citation graph update | `0 */6 * * *` | Every 6 hours |
| SENTINEL health check | `*/15 * * * *` | Every 15 minutes |
| SCOUT prompt refresh | `0 1 * * 1` | Monday 01:00 UTC |
| ORACLE-X recommendations | `0 8 * * 1` | Monday 08:00 UTC |

## LLM Configuration (Internal Processing)
| Use | Model | Max Tokens | Temperature |
|---|---|---|---|
| SIEVE extraction | claude-sonnet-4-20250514 | 1000 | 0.1 |
| ORACLE-X recommendations | claude-sonnet-4-20250514 | 2000 | 0.3 |

## Infrastructure
- **Database:** PostgreSQL — host/port/name from env vars, pool_size: 10, max_overflow: 20, timeout: 10s
- **Redis:** `REDIS_URL` env var, job queue: `oracle:jobs`, cache TTL: 48h
- **Environment vars:** `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `REDIS_URL`