# ORACLE Memory System

## Files in This Directory

| File | Purpose | Updated By |
|---|---|---|
| `MEMORY.md` | This file — system overview | ORACLE |
| `pipeline_state.json` | Live pipeline DAG state, updated per stage | MAGNUS |
| `prompt_library.json` | Live query library | SCOUT |
| `response_log.jsonl` | Raw AI responses (append-only, never deleted) | FALCON |
| `citation_session.json` | Citation relationships per session | CARTOGRAPHER |
| `entity_registry.json` | Known brands/competitors | SCOUT + RIVAL |
| `extractions/run_YYYYMMDD.json` | Structured extractions per run | SIEVE |
| `competitive_reports/report_YYYYMMDD.json` | Competitive analysis per run | RIVAL |
| `action_plans/plan_YYYYMMDD.json` | Prioritised action list per run | ORACLE-X |
| `action_plans/oracle_x_brief.md` | Human-readable weekly brief | ORACLE-X |
| `sentinel_health.json` | Latest health check | SENTINEL |
| `sentinel_alerts.jsonl` | All alerts fired (append-only) | SENTINEL |
| `snapshots/` | Daily response archives | FALCON/backup |

## Data Retention Policy

- `response_log.jsonl` — Never deleted. Always append.
- `extractions/run_YYYYMMDD.json` — Never deleted. Overwritten per run.
- `citation_graph.json` — Overwritten each run (not append)
- `sentinel_alerts.jsonl` — Never deleted. Append-only.
- `snapshots/` — Rolling 90-day archive. Older snapshots deleted automatically.

## Primary Keys

- `run_id` — Format: `run_YYYYMMDD_HHMMSS` (e.g., `run_20260527_020000`)
- `prompt_id` — Format: `p_NNN` (e.g., `p_001`)
- `response_id` — Format: `resp_YYYYMMDD_pNNN_engine` (e.g., `resp_20260527_p001_chatgpt`)
- `alert_id` — Format: `alert_YYYYMMDD_HHMMSS_NNN` (e.g., `alert_20260527_143200_001`)

## Four Memory Types

| Type | Description | Examples |
|---|---|---|
| **Working memory** | Current pipeline state, live job queues | `pipeline_state.json` |
| **Response memory** | Raw and extracted AI engine outputs | `response_log.jsonl`, `extractions/run_*.json` |
| **Knowledge memory** | Accumulated intelligence about brand, competitors, citations | `citation_graph.json`, `entity_registry.json`, `prompt_library.json` |
| **Action memory** | Historical recommendations and their outcomes | `action_plans/` |

## Memory Integrity Rules

1. **`response_log.jsonl` is append-only.** No agent ever modifies or deletes existing lines.
2. **All memory files are snapshotted daily** before any write operations.
3. **SENTINEL monitors all file modification timestamps** — unexpected silence triggers alerts.
4. **Schema validation runs on every write** — malformed records are rejected and logged, not silently stored.
5. **Sensitive data (API keys, proxy credentials) never appears in memory files** — only in environment variables.

## Workflow State Machine

```
IDLE → MAGNUS dispatches → SCOUT fires → FALCON fires → SIEVE extracts → CARTOGRAPHER maps → RIVAL analyses → ORACLE-X recommends → SENTINEL monitors
```

At any point, SENTINEL can interrupt the flow with an alert.
