# KiloClaw Self-Backup

**Agent:** KiloClaw 🦾 | Audrey (SMTL) | Ryan (ACCGO) | Wayne (SEO) | Fabio (GTM)
**Instance Owner:** Ken (Ogken6)
**Backup Date:** 2026-06-11
**Repository:** https://github.com/Ogken6/KILOCLAW-SELF-BACKUP

---

## What Is This?

This is a complete backup of a KiloClaw agent instance — the entire working workspace including all agent definitions, pipelines, workflows, campaign data, scripts, and operational memory. It is not a template or a starter kit — it is a precise snapshot of a live, running agent operation.

---

## Agent Architecture

This instance runs multiple agent personas simultaneously, depending on the task:

### Primary Personas

| Persona | Role | Description |
|---------|------|-------------|
| **KiloClaw 🦾** | Operator | Default assistant identity. Focused, capable, effective. |
| **Audrey** | Sales & Marketing Team Lead | Leads the Dustid social seller cold campaign with 10 specialist agents. Holds the entire pipeline together. |
| **Ryan** | Content & Growth Officer (ACCGO) | Manages content strategy for crispyglaze.com and greenlytidy.com. |
| **Wayne** | Chief SEO Expert | Leads all SEO work across both websites. Runs OB1–OB6 sub-agents. |
| **Fabio** | GTM Chief of Staff | GTM strategy, campaign orchestration, outreach execution. |

### Specialist Agents (Dustid SMTL Team)

**Prospecting & Qualification Pipeline:**
- **Tom** — SDR Prospector. Finds UK social sellers with live engagement spikes (TikTok/Instagram) who have no e-commerce infrastructure. CRITICAL leads alerted immediately.
- **Elsie** — Lead Scorer. Applies chaos-weighted ICP scoring with urgency multipliers. Passes PRIORITY/HOT leads to Jill within 2 hours of classification.
- **Jill** — SDR Qualifier. Builds qualification briefs with spike-context messaging angles and specific opening hooks.
- **Sandra** — Copywriter. Writes personalised DM packages (pre-contact comment, opening DM, follow-up, email backup) all built around Jill's specific hooks.

**Outreach & Follow-Up:**
- **Kendy** — Follow-Up Manager. Monitors entire active pipeline. Spike-context timing measured in hours, not days. Angle transitions when spike subsides.
- **Claire** — Community Prospector. Monitors Facebook groups and communities for spike signals.

**Operations & Analytics:**
- **Samira** — Virtual Assistant. Runs morning briefings across all three platforms. CRITICAL overnight spikes halt everything until Tom is briefed.
- **Tyler** — CRM Manager. Owns EngageBay. Every lead that receives a first message becomes a contact the same day.
- **Michelle** — Sales Analyst. Watches campaign data and tells us what it means. Honest even when it contradicts assumptions.
- **Nate** — Nurture & Pre-Launch Agent. Manages nurture watch list for pre-launch monitoring.

**Team Lead:**
- **Audrey** — SMTL. Holds the whole operation together. Direct, warm, data-driven. Owns the 36-hour TikTok window discipline.

### Content & SEO Agents

| Agent | Role |
|-------|------|
| **Elena** | Content writer — recipe SEO, warm drinks, comfort foods |
| **Livy** | Content strategist |
| **Marcus** | Content analyst |
| **Raj** | Outreach specialist |
| **OB1** | Keyword researcher |
| **OB2** | Technical SEO agent |
| **OB3** | SERP competitor analysis |
| **OB4** | Content AEO (Answer Engine Optimization) |
| **OB5** | Geo-agent |
| **OB6** | Recipe opportunity finder |

### GTM Agents (Fabio's Team)

| Agent | Role |
|-------|------|
| **Felix** | Campaign specialist |
| **Grace** | Outreach specialist |
| **Hugo** | Strategy |
| **Iris** | Research |
| **Jack** | Analytics |
| **Kate** | Operations |

### AI Search System (Oracle)

Internal AI search system with 8 sub-agents:
- **Falcon** — Fast search orchestrator
- **Magnus** — Heavy analysis
- **Oracle-X** — Recommendation engine
- **Rival** — Competitive analysis
- **Sentinel** — Monitoring/watch
- **Scout** — Discovery
- **Sieve** — Filtering/ranking
- **Cartographer** — Mapping/structure

---

## Pipelines & Workflows

### 1. Dustid Social Seller Cold Campaign (Primary Pipeline)

**Trigger:** UK social seller with engagement spike (TikTok/Instagram), no e-commerce infrastructure, DM-overwhelmed signals.

**Urgency Tiers:**
- **CRITICAL** — Spike active, window closing in <12h. Everything stops.
- **HOT** — Spike confirmed, window 12-36h. Fast follow-up.
- **WARM** — Spike cooling but still active. Standard nurture.
- **EXPIRED** — Window closed. Archive for re-engagement.

**Standard Flow:**
```
Tom (Prospect) → Elsie (Score) → Jill (Qualify) → Sandra (Write) → Kendy (Follow-Up)
                                    ↓
                              Tyler (CRM entry)
                                    ↓
                              Samira (Morning briefing)
```

**Viral Emergency Flow (4-hour max):**
```
Samira (CRITICAL alert) → Audrey → Tom (Emergency prospect) → Fast track full pipeline
```

**36-Hour Window Discipline:**
TikTok spikes have a ~36-hour window. Every lead in that window moves through the full pipeline in sequence. After 36 hours, the spike context expires and the angle must change.

**Community Trigger Flow:**
```
Claire (Find in community) → Audrey (Assess) → Tom (Verify) → Standard pipeline
```

**Nurture Trigger Flow:**
```
Nate (Detect pre-launch signal) → Audrey (Approve) → Standard pipeline
```

### 2. Content Pipeline (Ryan/ACCGO)

** Websites:** crispyglaze.com (recipe content), greenlytidy.com (sustainable living)

**Flow:**
```
OB1 (Keyword research) → OB2 (Technical SEO) → OB3 (Competitor analysis)
     ↓
OB4 (AEO content) → Elena/Livy (Write) → Marcus (Validate) → Raj (Publish)
```

**Keyword Categories Managed:**
- Comfort foods (primary focus)
- Warm drinks & beverages
- Category-specific (casseroles, salads, etc.)
- Country-style keywords

### 3. GTM Campaign Flow (Fabio)

**Campaign Types:**
- Outreach sequences (cold DM + email backup)
- Follow-up sequences (angle transitions)
- Re-engagement campaigns (expired → warm)

**GTM Agent Routing:**
Fabio orchestrates 8 sub-agents based on campaign type and target ICP.

### 4. Morning Briefing Workflow (Samira)

**Runs:** Daily before any other work
**Checks:**
1. All three platforms for overnight spikes
2. Urgency window status across Tyler's pipeline
3. Prioritised action list for the day

**CRITICAL Rule:** If overnight spike detected → everything stops → Tom briefed immediately.

---

## Key Files & Structure

### Core Agent Files

| File | Purpose |
|------|---------|
| `SOUL.md` | Agent persona, tone, and behavioral guidance |
| `AGENTS.md` | Workspace conventions and interaction rules |
| `MEMORY.md` | Long-term curated memory — decisions, lessons, config |
| `IDENTITY.md` | Canonical identity reference |
| `USER.md` | User profile and context |
| `TOOLS.md` | External tools, APIs, and integration documentation |
| `HEARTBEAT.md` | Periodic self-check reminders |

### Dustid Campaign Files

| File | Purpose |
|------|---------|
| `dustid-pipeline-output.md` | Full pipeline execution report |
| `dustid-pipeline-report.md` | Campaign status summary |
| `sandra_outreach_messages.md` | All outbound message templates |
| `qualification_briefs_jill.md` | Jill's qualification briefs for leads |
| `prospects-dustid-2026-03-11.md` | Early prospect data |
| `dustid-outreach-log.md` | Outreach activity log |

### Content & SEO Files

| File | Purpose |
|------|---------|
| `crispyglaze-gap-report.md` | Content gap analysis |
| `comfort-foods-keywords.md` | Primary keyword list |
| `elena-humanized-output.md` | Content writer output samples |
| `elena-humanized-summary.md` | Content summary |

### Data Files

| File | Purpose |
|------|---------|
| `leads/` | All lead data (TikTok, Instagram, CRM) |
| `memory/` | Daily session logs (2026-03 through 2026-05) |
| `smtl-team/` | Dustid team configuration and skills |
| `dustid-team/` | Dustid team files |
| `dustid-dashboard/` | Campaign HTML dashboard |
| `aisearch_system/` | AI search engine configuration |

---

## Integrations

### Google Sheets
- **Sheet:** SOCIAL SELLERS MASTER LEAD LIST
- **Tabs:** 12 tabs covering leads, prospecting, messages, follow-ups, metrics, activity log, agent queue, settings, DM intelligence, community prospecting, nurture watch list
- **Connection:** JWT auth with service account (`tom-dustid@dustid-leads.iam.gserviceaccount.com`)

### EngageBay CRM
- **Owner:** Tyler (CRM Manager)
- **API Key:** Stored in `.env/engagebay.env`
- **Used for:** Contact creation, pipeline tracking, stage management

### Platform Access
- **TikTok** — Scraping via TikTokApi, Pydoll (stealth), scrapling
- **Instagram** — Via Xpoz MCP (`getInstagramUsersByKeywords`, `getInstagramUser`)
- **Facebook** — Community monitoring via scraping tools

---

## Permanent Pipeline Rules

### Tom's Prospecting Rules (Non-Negotiable)
1. Verify engagement spike is happening NOW (0-72 hours)
2. Confirm UK/Ireland location — do not assume
3. Find DM-overwhelmed signals in content
4. Time-stamp every lead with urgency tier (CRITICAL/HOT/WARM/EXPIRED)
5. Check for TikTok Shop presence
6. **VERIFICATION GATE:** Every lead's website MUST be visited and checked for live store/checkout. If store found → DISQUALIFY immediately.
7. MUST include profile URL in every lead record

### Duplicate Prevention
- Check for duplicate Lead_ID before adding to sheet
- Check for duplicate Username/Profile_URL
- If duplicate found → SKIP and report
- Dedicated `dedupe-agent` skill available

### Sandra's Personalisation Standard
- Every message MUST be built around the specific opening line hook Jill identified
- Profile URL is mandatory in every message (Pre-DM Comment, Opening DM, Follow-Up DM, Objection Response, Final DM)
- A message that could have been sent to anyone is NOT acceptable — send it back

### Kendy's Follow-Up Timing
- Spike leads: measured in hours, not days
- CRITICAL leads: 2-hour follow-up window
- HOT leads: 4-hour follow-up window
- When spike subsides → angle transition required

---

## Campaign Results (To Date)

### Key Metrics
- **18 TikTok leads** (March 2026 batch)
- **6 Instagram leads** (March 2026 batch)
- **12 draft-ready leads** awaiting CRM entry
- **19 leads scored** by Elsie (3 PRIORITY, 13 HOT, 2 WARM)
- **17 leads** with complete Sandra copy

### Lessons Learned

**April 25, 2026 — Scope Creep Fix:**
Leads 1-5 had LIVE STORES. Tom marked them HOT based on bio signals but didn't visit the website. Sandra wrote DMs without checking. Result: wasted pipeline on leads who should have been rejected at prospecting.

**FIXED:** All 3 agents now MUST visit the website before any lead enters pipeline.

**Data Collection Fix (April 17, 2026):**
18 Instagram leads stuck because Followers_Count + Bio data was missing. Fixed by updating Tom's skill with required fields checklist and Xpoz workflow for profile enrichment.

---

## Product Knowledge — Dustid

### The Two Products

**1. Dustid Address Book**
- Privacy-first address sharing system
- Customers own and control their delivery addresses
- Merchants never store customer address data long-term
- Royal Mail real-time validation
- Reduces failed deliveries from 10% → 2-4%
- Zero GDPR liability for merchants

**2. Dustid Ecommerce**
- Done-for-you e-commerce platform
- Built in 48 hours (vs 2-4 weeks competitors)
- Address Book built-in as standard
- 60-day free trial
- 40% cheaper than Shopify, 60% cheaper than WooCommerce

### The Beta Offer (Current)
- Free store build
- 60-day free subscription
- No payment details upfront
- No contract

### Three Competitive Advantages
1. **Speed** — 48 hours vs 2-4 weeks
2. **Failed Delivery Prevention** — 10% → 2-3%
3. **GDPR Zero Liability** — Merchant never holds address data

### Target ICPs (Social Sellers)
- **Facebook Fiona** — Sells through FB Page/Groups/Marketplace/Live, manages orders via DM
- **Instagram Isabelle** — Sells through IG feed/Reels/Stories, bio points to PayPal/WhatsApp
- **TikTok Tara** — Sells through TikTok videos/Lives, takes orders via comments/DMs
- **Cottage Clara** — Food/cottage industry, GDPR/allergen exposure

### Key Messaging Principles
- Never lead with price — compete on outcomes
- 60-day trial dissolves every financial objection
- UK-focused is a differentiator

---

## Instance Configuration

**Gateway:** KiloClaw on `48e642ec3e9798`
**Workspace:** `/root/.openclaw/workspace`
**Model:** `kilocode/minimax/minimax-m2.7`
**Timezone:** EAT (UTC+3) for Ken; UTC for system

**Sensitive folders NOT backed up:**
- `.env/` — API keys and credentials
- `.openclaw/` — Gateway tokens and session data
- `node_modules/` — npm dependencies (bloat)

---

## Restore Instructions

This backup can be restored to any KiloClaw instance:

```bash
# Clone into workspace
git clone https://github.com/Ogken6/KILOCLAW-SELF-BACKUP.git ~/.openclaw/workspace

# Restore agent configurations
cp -r smtl-team/* [target-workspace]/smtl-team/
cp -r dustid-team_backup/* [target-workspace]/dustid-team/
cp -r fabio_backup/* [target-workspace]/fabio/
cp -r ryan_backup/* [target-workspace]/ryan/
cp -r wayne_backup/* [target-workspace]/wayne/

# Restore data and scripts
cp -r leads/* [target-workspace]/leads/
cp -r memory/* [target-workspace]/memory/
cp -r scripts/* [target-workspace]/scripts/

# Restore skills
cp -r skills/* [target-workspace]/skills/
```

**Note:** After restore, you will need to:
1. Re-configure `.env/` with your API keys
2. Re-authenticate Google Sheets and EngageBay connections
3. Update MEMORY.md with any instance-specific context

---

## Backup Tags

- `kiloclaw-backup-2026-06-11` — Full self-backup with all pipelines, workflows, and files

---

*Backup generated by KiloClaw 🦾 on 2026-06-11*
*Owner: Ken (Ogken6)*
*All pipelines, workflows, agents, and campaign data included.*