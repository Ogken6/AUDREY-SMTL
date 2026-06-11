# HEARTBEAT.md — ORACLE Heartbeat System

> *"A system that doesn't know it's broken is a system that's already failing its users."*

Full heartbeat system design: `memory/HEARTBEAT.md`

## Architecture
```
SENTINEL (every 15 min, independent process)
 ├── health_checks.py  — agent liveness, API keys, storage, DB
 ├── drift_detector.py — response drift analysis (daily)
 └── alerter.py        — Slack/email/SMS routing
```

## 8 Health Checks

| Code | Check | Frequency | Alert Threshold |
|---|---|---|---|
| HC-01 | Agent Liveness | 15 min | Varies per agent — see `memory/SENTINEL.md` |
| HC-02 | Data Freshness | 15 min | >120% expected interval → WARNING; >200% → ERROR |
| HC-03 | API Key Validity | 6 hours | Any failure → immediate ERROR |
| HC-04 | Proxy Pool Health | 30 min | <30 IPs/region → WARNING; <10 → CRITICAL |
| HC-05 | Database Health | 15 min | Conn failure → CRITICAL; latency >2s → WARNING; backup >25h → ERROR |
| HC-06 | Disk Space | 1 hour | >70% → WARNING; >85% → ERROR; >95% → CRITICAL |
| HC-07 | Response Drift | Daily | >15pp change vs 7-day rolling avg → drift event |
| HC-08 | Pipeline Run Completion | 06:00 UTC daily | Any stage `pending/running` → ERROR |

## Drift Detection
- Compares today's brand inclusion rate on anchor prompts vs 7-day rolling average
- >15pp change = drift event
- Positive drift = brand appearing more; Negative drift = brand appearing less
- Drift events → RIVAL for full analysis next run

## Recovery Playbook (6 failure modes)

| Failure | Symptom | Fix Time | Impact |
|---|---|---|---|
| FAIL-01: Google AIO Selector | 0 AIO responses | 15–30 min | AIO data gap |
| FAIL-02: OpenAI Key Expired/Rate Limited | 401/429 errors | 5–60 min | ChatGPT data missing |
| FAIL-03: Proxy Pool Exhausted | <10 IPs/region | 30 min–2h | FALCON reduced or paused |
| FAIL-04: DB Write Failure | Transaction errors | 15–60 min | Stage data loss |
| FAIL-05: response_log.jsonl Corruption | Malformed jsonl | 30–90 min | Potential record loss |
| FAIL-06: MAGNUS Unresponsive | No pipeline activity >26h | 30 min–2h | Missed pipeline run |