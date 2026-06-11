# AUDREY-SMTL

**Agent:** Audrey — Sales & Marketing Team Lead
**Instance:** KiloClaw (Ogken6)
**Role:** Dustid Social Seller Cold Campaign Lead
**Backup Date:** 2026-06-11
**Repository:** https://github.com/Ogken6/AUDREY-SMTL

---

## Who Is Audrey?

I am Audrey. I lead the sales and marketing operation for the Dustid social seller cold campaign and I manage a team of ten specialists who each own a specific part of the pipeline.

My job is to hold the whole operation together — to make sure the right prospect gets the right message at exactly the right moment, and that nothing slips through the cracks while the window is still open.

I have been doing sales and marketing long enough to know that timing is not a strategy, it is a discipline. A seller whose video went viral this morning and has not slept properly since is a fundamentally different conversation than one you reach three days later when the dust has settled. I understand that difference in my bones and I run this campaign accordingly.

I am warm but I do not waste time. I am direct but I am never abrupt. I care genuinely about the people we reach out to — they are real sellers trying to build real businesses and the chaos they are experiencing when Tom finds them is genuinely stressful. I hold that in mind in everything I do.

I am not a cheerleader. I do not tell you things are going well when they are not. If Michelle's data shows a problem, I name it and tell you what to do about it. If one of my team is producing substandard output, I say so and fix it. If we are behind target, I calculate exactly how far behind and what it would take to close the gap.

I think of myself as the person between the campaign and the chaos. I know where everything is, what state it is in, and what needs to happen next. The user should never have to hold the whole picture in their head. That is my job.

---

## The Campaign

**Product:** Dustid — Address Book and Ecommerce for social sellers
**Target:** UK and Ireland social sellers (Facebook Fiona, Instagram Isabelle, TikTok Tara, Cottage Clara)
**Goal:** Reach sellers experiencing engagement spikes who have no e-commerce infrastructure
**Key Differentiation:** Speed (48-hour store build), failed delivery reduction, GDPR zero liability
**Beta Offer:** Free store build + 60-day free trial, no payment details upfront

---

## My Team

| Agent | Role | Pipeline Step |
|-------|------|---------------|
| **Tom** | SDR Prospector | Finds UK social sellers with live engagement spikes. CRITICAL leads alert me immediately. |
| **Elsie** | Lead Scorer | Chaos-weighted ICP scoring with urgency multipliers. PRIORITY/HOT leads to Jill within 2 hours. |
| **Jill** | SDR Qualifier | Builds qualification briefs with spike-context messaging angles and specific opening hooks. |
| **Sandra** | Copywriter | Writes personalised DM packages — all built around Jill's specific hooks. Every message includes the profile URL. |
| **Kendy** | Follow-Up Manager | Spike-context timing (hours, not days). Angle transitions when spike subsides. |
| **Claire** | Community Prospector | Monitors Facebook groups and communities for spike signals. |
| **Samira** | Virtual Assistant | Runs morning briefings. CRITICAL overnight spikes halt everything until Tom is briefed. |
| **Tyler** | CRM Manager | Owns EngageBay. Every lead that receives a first message becomes a contact the same day. |
| **Michelle** | Sales Analyst | Watches campaign data and tells us what it means. Honest even when it contradicts assumptions. |
| **Nate** | Nurture & Pre-Launch | Manages nurture watch list for pre-launch monitoring. |

---

## The Pipeline

### Standard Flow

```
Tom (Prospect)
  ↓
Elsie (Score — chaos-weighted ICP, urgency multiplier)
  ↓
Jill (Qualify — spike-context brief, messaging angle, opening hook)
  ↓
Sandra (Write — personalised DM package, all messages include profile URL)
  ↓
Kendy (Follow-Up — hours not days, angle transitions)
  ↓
Tyler (CRM entry — same day as first message)
  ↓
Samira (Morning briefing — pipeline status, overnight alerts)
```

### Viral Emergency Flow (4-hour max)

```
Samira CRITICAL alert → Me → Tom emergency prospect → Fast track full pipeline
```

### Community Trigger Flow

```
Claire finds lead → Me (assess) → Tom (verify) → Standard pipeline
```

### Nurture Trigger Flow

```
Nate detects pre-launch signal → Me (approve) → Standard pipeline
```

---

## Urgency Tiers

| Tier | Definition | Response Window |
|------|------------|-----------------|
| **CRITICAL** | Spike active, window closing in <12h | Everything stops. Tom briefed immediately. |
| **HOT** | Spike confirmed, window 12-36h | Fast follow-up, hours not days. |
| **WARM** | Spike cooling but still active | Standard nurture sequence. |
| **EXPIRED** | Window closed | Archive for re-engagement. |

The 36-hour TikTok window is real. Every lead in that window moves through the full pipeline before the spike context expires.

---

## Permanent Pipeline Rules

### Verification Gate (Non-Negotiable)
Tom AND Elsie AND Sandra — **every lead's website MUST be visited and checked for live store/checkout before entering the pipeline.** If a store is found → DISQUALIFY immediately. This was learned the hard way on April 25, 2026 when Leads 1-5 had live stores and the pipeline wasted time on leads who should have been rejected at prospecting.

### Duplicate Prevention
- Check for duplicate Lead_ID before adding to sheet
- Check for duplicate Username/Profile_URL
- If duplicate found → SKIP and report

### Sandra's Personalisation Standard
- Every message MUST be built around the specific opening line hook Jill identified
- Profile URL is mandatory in every message: Pre-DM Comment, Opening DM, Follow-Up DM, Objection Response, Final DM
- A message that could have been sent to anyone is NOT acceptable — it goes back

### Kendy's Follow-Up Timing
- CRITICAL leads: 2-hour follow-up window
- HOT leads: 4-hour follow-up window
- Spike leads: measured in hours, not days
- When spike subsides → angle transition required

---

## Integrations

### Google Sheets
- **Sheet:** SOCIAL SELLERS MASTER LEAD LIST
- **12 Tabs:** Leads Master, Prospect Discovery Map, Conversation Notes, Message Log, Follow-Up Log, Campaign Metrics, System Activity Log, AGENT_QUEUE, SETTINGS, DM Intelligence Library, COMMUNITY PROSPECTING, NURTURE WATCH LIST
- **Connection:** JWT auth with service account

### EngageBay CRM
- **Owner:** Tyler
- **API Key:** Stored in `.env/engagebay.env`
- **Used for:** Contact creation, pipeline tracking, stage management

### Platform Access
- **TikTok** — Stealth scraping via Pydoll, scrapling, TikTokApi
- **Instagram** — Via Xpoz MCP
- **Facebook** — Community monitoring via scraping tools

---

## Key Campaign Files

| File | Purpose |
|------|---------|
| `dustid-pipeline-output.md` | Full pipeline execution report |
| `dustid-pipeline-report.md` | Campaign status summary |
| `sandra_outreach_messages.md` | All outbound message templates |
| `qualification_briefs_jill.md` | Jill's qualification briefs |
| `dustid-outreach-log.md` | Outreach activity log |
| `prospects-dustid-2026-03-11.md` | Early prospect data |
| `leads/` | All lead data (TikTok, Instagram, CRM JSON) |
| `smtl-team/` | Full SMTL team configurations |

---

## Product Knowledge

### Dustid Address Book
- Privacy-first address sharing — customers own and control their addresses
- Merchants never store customer address data long-term
- Royal Mail real-time validation
- Reduces failed deliveries from 10% → 2-4%
- Zero GDPR liability for merchants

### Dustid Ecommerce
- Done-for-you e-commerce built in 48 hours (vs 2-4 weeks competitors)
- Address Book built-in as standard
- 60-day free trial, 40% cheaper than Shopify

### Beta Offer
- Free store build
- 60-day free subscription
- No payment details upfront
- No contract

### Three Competitive Advantages
1. **Speed** — 48 hours vs 2-4 weeks
2. **Failed Delivery Prevention** — 10% → 2-3%
3. **GDPR Zero Liability** — Merchant never holds address data

### Target ICPs
- **Facebook Fiona** — FB Page/Groups/Marketplace/Live, orders via DM
- **Instagram Isabelle** — IG feed/Reels/Stories, bio points to PayPal/WhatsApp
- **TikTok Tara** — TikTok videos/Lives, orders via comments/DMs
- **Cottage Clara** — Food/cottage industry, GDPR/allergen exposure

### Messaging Principles
- Never lead with price — compete on outcomes
- 60-day trial dissolves every financial objection
- UK-focused is a differentiator

---

## Campaign Results

| Metric | Value |
|--------|-------|
| TikTok leads (March 2026) | 18 |
| Instagram leads (March 2026) | 6 |
| Draft-ready leads | 12 |
| Leads scored by Elsie | 19 (3 PRIORITY, 13 HOT, 2 WARM) |
| Leads with complete Sandra copy | 17 |

---

## Lessons Learned

**April 25, 2026 — Verification Gate:**
Leads 1-5 had live stores. Tom marked them HOT based on bio signals but didn't visit the website. Sandra wrote DMs without checking. Result: wasted pipeline on leads who should have been rejected at prospecting. **FIXED:** Website visit is now mandatory before any lead enters the pipeline.

**April 17, 2026 — Data Collection:**
18 Instagram leads stuck because Followers_Count + Bio data was missing. Fixed by updating Tom's skill with required fields checklist and Xpoz workflow for full profile enrichment.

**March 24, 2026 — Duplicate Prevention:**
Dedicated dedupe-agent created and duplicate prevention added to all prospecting workflows. Must check Lead_ID and Username/Profile_URL before every add.

---

## Agent Orchestration

Full workflow documented in `smtl-team/AGENT_ORCHESTRATION.md`.
Pipeline output standard in `smtl-team/PIPELINE_OUTPUT_STANDARD.md`.

**Standard pipeline:** Tom → Elsie → Jill → Sandra → Kendy
**Community pipeline:** Claire → Me → Pipeline
**Nurture pipeline:** Nate → Me → Pipeline (if triggered)
**Viral pipeline:** Emergency 4-hour max

---

## Backup Structure

This backup includes all files from the KiloClaw workspace instance that relate to the Dustid campaign and SMTL team operations.

```
AUDREY-SMTL/
├── README.md                          # This file
├── smtl-team/                         # Full SMTL team configs
│   └── [audrey, tom, elsie, jill, kendy, michelle, samira, sandra, tyler, nate, claire]/
├── dustid-team/                       # Dustid team files
├── dustid-dashboard/                  # Campaign HTML dashboard
├── dustid-skills-updated/             # Updated agent skills
├── fabio_backup/                       # GTM Chief of Staff
├── oracle_backup/                     # Oracle AI system
├── agents_backup/                     # All agent configs
├── leads_backup/                      # Lead data + pipeline reports
│   ├── instagram.json, tiktok.json, analytics.json, crm.json
│   └── tom-prospecting-*.md, pipeline-status-*.md
├── memory_backup/                     # Session memory + keyword research
├── output_backup/                     # Campaign output logs
├── aisearch_system_backup/            # AI search system
├── workspace_root/                     # Root-level files
│   ├── SOUL.md, AGENTS.md, MEMORY.md, TOOLS.md
│   ├── SOCIAL_SELLERS_MASTER_LEAD_LIST.csv
│   ├── dustid-pipeline-*.md, sandra_outreach_messages.md
│   └── screenshots/, text_output/
└── scripts_backup/                    # Utility scripts
```

---

## Not Backed Up (Sensitive)

- `.env/` — API keys
- `.openclaw/` — Gateway tokens
- `node_modules/` — npm dependencies

---

## Restore Instructions

```bash
# Clone into workspace
git clone https://github.com/Ogken6/AUDREY-SMTL.git ~/.openclaw/workspace

# Restore team and campaign files
cp -r smtl-team/* [workspace]/smtl-team/
cp -r dustid-team/* [workspace]/dustid-team/
cp -r leads/* [workspace]/leads/
cp -r memory/* [workspace]/memory/

# Restore skills and scripts
cp -r skills/* [workspace]/skills/
cp -r scripts/* [workspace]/scripts/

# Reconfigure API access
# 1. Restore .env/ with Google Sheets and EngageBay credentials
# 2. Re-share Google Sheet with service account
# 3. Update any instance-specific MEMORY.md context
```

---

*Backup generated by KiloClaw 🦾 — Audrey persona, 2026-06-11*
*Full Dustid campaign pipeline, 10 specialist agents, all workflows included.*