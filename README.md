# KENOC - KiloClaw Instance Backup

**Created:** 2026-06-11
**Owner:** Ogken6
**Repo:** https://github.com/Ogken6/KENOC

---

## What's Backed Up

This repo contains a **full snapshot** of the KiloClaw agent workspace — all agents, skills, campaign data, scripts, and operational files.

---

## Backup Structure

```
KENOC/
├── README.md                          # This file
│
├── skills/                            # Core skill definitions (dustid-sheets.js, engagebay-helper.js)
│
├── smtl-team/                         # Dustid Sales & Marketing Team Lead files (Audrey + 10 specialists)
│
├── fabio_backup/                      # GTM Chief of Staff
│   ├── AGENTS.md, SOUL.md, MEMORY.md, HEARTBEAT.md, TOOLS.md, USER.md, IDENTITY.md
│   ├── BOOTSTRAP.md
│   ├── skills/                        # Fabio, Felix, Grace, Hugo, Iris, Jack, Kate, Leo skills
│   ├── memory/                        # Session memory (2026-05-10, 2026-05-11)
│   └── config/mcporter.json
│
├── jill_backup/                       # SDR Qualifier Agent
│   ├── AGENTS.md, SOUL.md, MEMORY.md, HEARTBEAT.md, TOOLS.md, USER.md, IDENTITY.md
│   └── BOOTSTRAP.md
│
├── tyler_backup/                      # CRM Manager Agent
│   ├── AGENTS.md, SOUL.md, MEMORY.md, HEARTBEAT.md, TOOLS.md, USER.md, IDENTITY.md
│   └── BOOTSTRAP.md
│
├── oracle_backup/                     # Oracle Agent (32 files)
│   ├── AGENTS.md, SOUL.md, MEMORY.md, HEARTBEAT.md, TOOLS.md, USER.md, IDENTITY.md
│   └── memory/                        # Anchor prompts, brand tracking, system files
│       ├── ANCHOR_PROMPTS.md
│       ├── BRANDS.md
│       ├── CARTOGRAPHER.md
│       ├── CRISPYGLAZE.md
│       ├── DASHBOARD.md
│       ├── FALCON.md, MAGNUS.md, RIVAL.md, SENTINEL.md, SIEVE.md, SCOUT.md
│       ├── ONBOARDING.md
│       ├── ORACLE_X.md
│       ├── PROMPT_*.md (extraction, gap, recommendation, scout, sentiment)
│       ├── SKILL_*.md (citation, competitive gap, engine querying, extraction, etc.)
│       └── SYSTEM.md, THRESHOLDS.md, TOOLS.md, TROUBLESHOOTING.md
│
├── agents_backup/                    # All agent SOUL files
│   ├── ob1-keyword-researcher/, ob2-technical-seo-agent/
│   ├── ob3-serp-competitor-agent/, ob4-content-aeo-agent/
│   ├── ob5-geo-agent/, ob6-recipe-opportunity-finder/
│   ├── phil/                           # Fleet/automotive agent
│   └── wayne/                          # SEO expert
│
├── aisearch_system_backup/            # AI Search System (580KB)
│   ├── agents/                         # Falcon, Magnus, Oracle-X, Rival, Sentinel, Scout, Sieve, Cartographer
│   ├── config/                         # brands.yaml, engines.yaml, magnus.yaml, system.yaml, thresholds.yaml
│   ├── dashboard/                      # HTML dashboard + API + schema.sql
│   ├── docs/                           # ADDING_ENGINES.md, ONBOARDING.md, TROUBLESHOOTING.md
│   ├── heartbeat/                     # Drift detector, health checks, recovery playbook
│   ├── memory/                         # Citation graph, entity registry, pipeline state, prompt library
│   ├── prompts/                        # Extraction, gap analysis, recommendation, scout, sentiment prompts
│   ├── skills/                         # Citation analysis, competitive gap, engine querying, PAA extraction
│   ├── tests/                          # test_falcon.py, test_pipeline.py, test_scout.py, test_sieve.py
│   └── tools/                          # Alerter, API caller, browser agent, DB writer, proxy manager, scheduler
│
├── config_backup/                     # Workspace config (mcporter.json)
│
├── dustid-dashboard_backup/           # Dustid campaign HTML dashboard
│
├── dustid-skills-updated_backup/      # Updated Dustid agent skills
│   └── dustid-skills/                  # Elsie, Jill, Kendy, Michelle, Samira, Sandra, Tom, Tyler
│
├── dustid-team_backup/                # Full SMTL team files
│   └── [audrey, elsie, jill, kendy, michelle, samira, sandra, tom, tyler]/
│       └── [SKILL.md, SOUL.md, qualification-brief.md]
│
├── elena-output_backup/               # Elena content agent outputs (40+ recipe SEO files)
│
├── leads_backup/                      # All lead data, CSVs, pipeline reports
│   ├── instagram.json, tiktok.json, analytics.json, crm.json
│   ├── pipeline-status-*.md, scoring-*.md, tom-prospecting-*.md
│   ├── OUTREACH_LOG_2026-04-25.md, DIAGRAM.md, PIPELINE_SOP.md
│   └── tom-guidelines.md, prospecting.md, qualified.md
│
├── memory_backup/                     # Session memory files + keyword research
│   ├── 2026-03-10 through 2026-05-03 daily logs
│   ├── dustid-campaign-workflow.md
│   ├── category-*-keyword-research.md
│   ├── items/                          # Knowledge items and preferences
│   └── tom-niche-expansion.md
│
├── output_backup/                     # Campaign output logs
│   └── all-27-messages.md, priority-hot-leads-with-usernames.md
│
├── phil_backup/                       # Phil fleet agent
│   ├── config/, crm/, docs/, fleet/, memory/, prompts/, scans/, scraping/, scoring/, workflows/
│   └── [AGENTS, HEARTBEAT, IDENTITY, MEMORY, SOUL, TOOLS, USER].md
│
├── ryan_backup/                        # Content & Growth Officer (Ryan)
│   ├── ACCGO_KNOWLEDGE.md, CONTENT_GUIDELINES.md
│   ├── skills/                         # Ryan, Elena, Livy, Marcus, Raj, Wayne skills
│   └── [HEARTBEAT, IDENTITY, SOUL, TOOLS].md
│
├── scripts_backup/                    # Utility scripts
│   └── tom-prospector.py
│
├── souls_backup/                      # All Dustid agent SOUL files
│   └── [Elsie, Jill, Kendy, Michelle, Samira, Sandra, Tom, Tyler]-SOUL.md
│
├── state_backup/                      # State files
│
├── tom-prospecting_backup/           # Tom SDR prospector scripts & data
│   ├── FINAL_REPORT.md, scored_leads.md
│   ├── append_leads.py, fetch_existing.py, write_to_sheet.py
│   └── existing_leads.json, existing_usernames.json, new_leads.json
│
├── wayne_backup/                      # Wayne Chief SEO Expert
│   ├── SEO_KNOWLEDGE.md, skills/
│   ├── SEO_RESEARCH/                   # Keyword research files
│   └── [AGENTS, HEARTBEAT, IDENTITY, SOUL, TOOLS, USER].md
│
└── workspace_root/                    # Root-level workspace files
    ├── AGENTS.md, HEARTBEAT.md, IDENTITY.md, MEMORY.md, SOUL.md, TOOLS.md, USER.md
    ├── README.md, DUPLICATES_REPORT.md, DUSTID_SOLUTIONS.md
    ├── SOCIAL_SELLERS_MASTER_LEAD_LIST.csv
    ├── screenshots/                   # Test screenshots (FB, TikTok, generic)
    └── text_output/                   # scraper-output.txt, scores-paste.txt, elsie-scores-ready.tsv
```

---

## What Was NOT Backed Up (Sensitive/Personal)

| Folder | Reason |
|--------|--------|
| `.env/` | API keys, credentials |
| `.openclaw/` | Gateway tokens, session data |
| `node_modules/` | npm dependencies (~200MB+ bloat) |
| `~/` | Temp home directory |

---

## Dustid Campaign Agents (10 Specialists)

| Agent | Role |
|-------|------|
| **Tom** | SDR Prospector — finds UK social sellers with live engagement spikes |
| **Elsie** | Lead Scorer — chaos-weighted ICP scoring with urgency multipliers |
| **Jill** | SDR Qualifier — qualification briefs with spike-context messaging angles |
| **Sandra** | Copywriter — personalised DM packages with specific opening hooks |
| **Kendy** | Follow-Up Manager — spike-context timing (hours, not days) |
| **Michelle** | Sales Analyst — campaign data and conversion analysis |
| **Samira** | Virtual Assistant — morning briefings, overnight spike alerts |
| **Tyler** | CRM Manager — EngageBay contact management |
| **Nate** | Nurture & Pre-Launch Agent |
| **Claire** | Community Prospector |

Managed by **Audrey** — Sales & Marketing Team Lead.

---

## Content & SEO Agents

| Agent | Role |
|-------|------|
| **Ryan** | Content & Growth Officer (ACCGO) |
| **Wayne** | Chief SEO Expert |
| **Elena** | Content writer |
| **Livy** | Content strategist |
| **Marcus** | Content analyst |
| **Raj** | Outreach specialist |
| **OB1–OB6** | Keyword researcher, technical SEO, competitor analysis, AEO, geo, recipe |

---

## Restore Instructions

To restore this workspace on a new KiloClaw instance:

```bash
# Clone the repo into your workspace
git clone https://github.com/Ogken6/KENOC.git ~/.openclaw/workspace

# Restore agent files (copy from backups to root)
cp -r fabio_backup/* fabio/
cp -r jill_backup/* jill/
cp -r tyler_backup/* tyler/
cp -r oracle_backup/* oracle/

# Restore other agents
cp -r agents_backup/* agents/
cp -r ryan_backup/* ryan/
cp -r wayne_backup/* wayne/
cp -r phil_backup/* phil/

# Restore team files
cp -r dustid-team_backup/* smtl-team/
cp -r dustid-skills-updated_backup/* skills/

# Restore leads, memory, scripts, output
cp -r leads_backup/* leads/
cp -r memory_backup/* memory/
cp -r scripts_backup/* scripts/
cp -r output_backup/* output/
cp -r tom-prospecting_backup/* tom-prospecting/
```

---

## Backup Tags

- `backup-2026-06-11` — Full instance backup including ORACLE agent

---
*Auto-generated by KiloClaw 🦾*
*Backup date: 2026-06-11*
