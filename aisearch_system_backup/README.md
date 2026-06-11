# ORACLE — Omniscient Real-time AI Citation & Landscape Engine

ORACLE is a fully autonomous, multi-agent AI search visibility and analytics system. It monitors how brands, products, and entities appear inside AI-generated answers across every major AI engine — ChatGPT, Perplexity, Google AI Overviews, Gemini, Claude, and Copilot — and converts that raw intelligence into actionable recommendations.

---

## The Agent Roster

| Codename | Role |
|---|---|
| **MAGNUS** | Chief of Staff — orchestrates all agents, owns the pipeline |
| **SCOUT** | Prompt Intelligence Agent — builds and evolves the prompt library |
| **FALCON** | Multi-Engine Query Agent — fires queries across AI platforms |
| **SIEVE** | Parsing & Extraction Agent — structures raw AI responses |
| **CARTOGRAPHER** | Citation Graph Agent — maps the source web behind AI answers |
| **RIVAL** | Competitive Intelligence Agent — calculates share of voice, gaps |
| **ORACLE-X** | Recommendation Agent — turns data into actions |
| **SENTINEL** | Heartbeat Agent — monitors system health, detects drift |

---

## Quick Start

```bash
# Configure your brand
cp config/brands.yaml.example config/brands.yaml

# Set API keys
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export PROXY_API_KEY=...

# Initialise the database
psql -f dashboard/schema.sql

# Start SENTINEL (heartbeat daemon)
python heartbeat/health_checks.py --daemon

# Run MAGNUS to start the pipeline
python agents/magnus.py --run-now
```
