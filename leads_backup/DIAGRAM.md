# Dustid Sales Pipeline - Storage & Execution Diagram

## Full Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DUSTID SALES PIPELINE                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              STORAGE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   leads/                                                                    │
│   ├── index.md           ← MASTER (overview + quick stats)                  │
│   ├── PIPELINE_SOP.md    ← GUIDELINES (how to request data)               │
│   │                                                                      │
│   ├── prospecting.md     ← TOM (raw prospects)                             │
│   │                                                                      │
│   ├── scoring.md         ← ELSIE (ICP-scored leads)                        │
│   │                      ├── Hot (70+)                                     │
│   │                      ├── Warm (40-69)                                  │
│   │                      ├── Cold (<40)                                    │
│   │                      └── Pending                                        │
│   │                                                                      │
│   ├── qualified.md       ← JILL (human-qualified leads)                    │
│   │                                                                      │
│   ├── outreach/                                                          │
│   │   ├── drafts/       ← Pre-approval messages                           │
│   │   └── sent.md       ← SANDRA (sent messages)                          │
│   │                                                                      │
│   ├── follow-up.md       ← KENDY (follow-up activities)                    │
│   │                                                                      │
│   ├── crm.json          ← TYLER (CRM entries) ← JSON                      │
│   │                                                                      │
│   └── analytics.json    ← MICHELLE (metrics) ← JSON                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            EXECUTION FLOW                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │   TOM    │ →  │  ELSIE  │ →  │   JILL  │ →  │ SANDRA   │             │
│   │ Prospector│    │  Scorer  │    │ Qualifier│    │Copywriter│             │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘             │
│        │               │               │               │                    │
│        ↓               ↓               ↓               ↓                    │
│   prospecting.md   scoring.md      qualified.md    outreach/                │
│                                                           │                  │
│   INPUT:              INPUT:           INPUT:          INPUT:               │
│   - Niche            - prospecting.md  - scoring.md     - qualified.md      │
│   - Platform         - ICP matrix       - Human verify  - Writing           │
│   - Keywords        - Score            - Interest       guidelines          │
│                                      check                               │
│                                                           ↓                  │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │  KENDY  │ →  │  TYLER   │ →  │ MICHELLE │    │   KEN    │             │
│   │Follow-Up │    │   CRM    │    │ Analytics│    │  (Human) │             │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘    └──────────┘             │
│        │               │               │                                    │
│        ↓               ↓               ↓                                    │
│   follow-up.md    crm.json       analytics.json                            │
│                                                                             │
│   INPUT:              INPUT:           INPUT:                               │
│   - outreach/sent.md - sent.md       - All stages                          │
│   - Response         - follow-up.md  - Metrics                             │
│   - Time             - Outcomes       calculation                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA REQUEST COMMANDS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   # All leads overview                                                      │
│   cat leads/index.md                                                        │
│                                                                             │
│   # Scored leads (Elsie)                                                   │
│   cat leads/scoring.md                                                      │
│                                                                             │
│   # Sent messages (Sandra)                                                  │
│   cat leads/outreach/sent.md                                                │
│                                                                             │
│   # Follow-ups (Kendy)                                                     │
│   cat leads/follow-up.md                                                    │
│                                                                             │
│   # CRM (Tyler)                                                            │
│   cat leads/crm.json                                                        │
│                                                                             │
│   # Analytics (Michelle)                                                   │
│   cat leads/analytics.json                                                  │
│                                                                             │
│   # Full SOP                                                                │
│   cat leads/PIPELINE_SOP.md                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        STORAGE FORMAT SUMMARY                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   MARKDOWN (.md)          │  JSON (.json)                                  │
│   ─────────────────────   │  ────────────                                   │
│   • prospecting.md         │  • crm.json                                    │
│   • scoring.md             │  • analytics.json                               │
│   • qualified.md                                                          │
│   • outreach/sent.md                                                     │
│   • follow-up.md                                                        │
│                                                                             │
│   Why Markdown:            │  Why JSON:                                      │
│   - Agent outputs         │  - Structured data                              │
│   - Human readability     │  - Fast search/filter                           │
│   - Easy to edit          │  - Complex metrics                             │
│   - Tables format well    │  - CRM fields                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

---
*Last updated: 2026-03-12 | Location: leads/PIPELINE_SOP.md*
