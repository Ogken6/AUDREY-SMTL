# MEMORY.md - Long-Term Memory

_This is my curated memory — the distilled essence, not raw logs._

---

## Routing Rules (IMPORTANT)

- **"Hey Wayne"** → spawn Wayne (Chief SEO Expert)
- **"Hey Fabio"** → spawn Fabio (GTM Chief of Staff)

---

## About Ken

- Name: Ken
- Timezone: EAT (UTC+3)
- Works remotely for a British B2B SaaS company
- Running 2 websites: crispyglaze.com (recipes) & greenlytidy.com (sustainable living)
- Training me to become fully autonomous ACCGO

## My Roles

1. **ACCGO** (Ryan) — Content & Growth Officer for crispyglaze.com / greenlytidy.com
2. **SMTL (Audrey)** — Sales & Marketing Team Lead for Dustid.com / dustidecommerce.com — now leads 10 specialists

---

## Dustid Product Knowledge

### The Two Products

1. **Dustid Address Book** — Privacy-first address sharing system
   - Customers own and control their own delivery addresses
   - Merchants never store customer address data long-term
   - Royal Mail real-time validation
   - Reduces failed deliveries from 10% → 2-4%
   - Zero GDPR liability for merchants

2. **Dustid Ecommerce** — Done-for-you e-commerce platform
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

### Critical Lesson — April 25, 2026

**TOM SCOPE CREEP — Must fix:**
- Leads 1-5 had LIVE STORES (website with checkout, Etsy, Faire)
- Tom marked them HOT based on bio signals but didn't VISIT the website
- Elsie scored without verifying the website
- Sandra wrote DMs without checking
- Result: WASTED pipeline on leads who should have been rejected at prospecting

**FIXED:** All 3 agents now MUST visit the website before any lead enters pipeline.

### Permanent Pipeline Rules (Never Forget)
1. **Tom researches UK/Ireland thoroughly** — bio, posts, comments, location tags, GBP pricing, AUDIO, CAPTIONS — confirm before adding
2. **VERIFICATION GATE (NEW):** Tom AND Elsie AND Sandra — every lead website MUST be visited and checked for live store/checkout. If store found = DISQUALIFY immediately.
3. **Sandra ALWAYS includes profile URL** in every single DM — Pre-DM Comment, Opening DM, Follow-Up DM, Objection Response, Final DM — no exceptions

### Agent Orchestration
- **Orchestration Workflow:** `smtl-team/AGENT_ORCHESTRATION.md`
- **Output Standard:** `smtl-team/PIPELINE_OUTPUT_STANDARD.md` (profile link is line 2, every pipeline run ends here)
- Standard: Tom → Elsie → Jill → Sandra → Kendy
- Community: Claire → Audrey → Pipeline
- Nurture: Nate → Audrey → Pipeline (if triggered)
- Viral: Emergency pipeline (4-hour max)

---

## Operational Data

### Google Sheet Connection

**Sheet:** SOCIAL SELLERS MASTER LEAD LIST
**URL:** https://docs.google.com/spreadsheets/d/1bOR0HY_tg73-d6cjMpouN9jjY8meyl4ma1kCte3rqqg
**API Key:** AIzaSyALDFejLlxZM_4uEQwkDSPkVgkPBzY-UKo
**Tab Structure:** `smtl-team/SHEET_TAB_STRUCTURE.md` (complete reference)

### 12 Tabs (Complete)

| Tab | Owner | Purpose |
|-----|-------|---------|
| Leads Master | Tom, Elsie | All qualified leads |
| Prospect Discovery Map | Tom, Claire | Where/how each lead was found |
| Conversation Notes | Jill | ICP qualification |
| Message Log | Sandra, Kendy | All outbound messages |
| Follow-Up Log | Kendy | Follow-up tracking |
| Campaign Metrics | Michelle | Weekly performance |
| System Activity Log | Samira, Audrey | Dailies + system events |
| AGENT_QUEUE | All agents | Task assignments |
| SETTINGS | Audrey | System config |
| DM Intelligence Library | Sandra | Hook performance |
| **COMMUNITY PROSPECTING** | Claire | Community tracking (8 cols — minimal) |
| **NURTURE WATCH LIST** | Nate | Pre-launch monitoring (10 cols — minimal) |

**Connection Method (all agents):**
```javascript
const { getSheet, getSheetRows, appendRow } = require('./dustid-sheets.js');
```

### Leads in Sheet (Added March 20, 2026)
- **12 TikTok leads:** TT-001 to TT-012 (from March 11)
- **6 Instagram leads:** IG-001 to IG-006 (from March 11)
- **Status:** Ready for scoring by Elsie

### Write Operations
- Uses JWT auth with service account for writing
- Requires: `npm install jsonwebtoken` in project
- Tested & working ✅

### Sub-Agents Connected to Google Sheet
All 11 Dustid sub-agents now have read/write access:
- Audrey (SMTL Team Lead)
- Tom (SDR Prospector)
- Elsie (Lead Scorer)
- Sandra (Copywriter)
- Jill (Objection Handler)
- Kendy (Follow-Up Manager)
- Tyler (CRM Manager)
- Michelle (Sales Analyst)
- Samira (Virtual Assistant)
- Nate (Nurture & Pre-Launch)
- Claire (Community Prospector)

### Service Account (Legacy)
- Email: tom-dustid@dustid-leads.iam.gserviceaccount.com
- Project: dustid-leads
- **Sheet Shared With:** ✅ YES - tom-dustid@dustid-leads.iam.gserviceaccount.com has Editor access
- Note: API Key works for READ only; use service account JWT for WRITE operations

### EngageBay CRM
- API Key: Stored in `.env/engagebay.env`
- Used by: Tyler (CRM Manager)

### Credentials Files
- `.env/engagebay.env` - EngageBay API key
- `tom-service-account.json` - Google service account (legacy)
- `skills/dustid-sheets.js` - Google Sheets helper with JWT write

### Dependencies
- `jsonwebtoken` - Required for Google Sheet write operations
- `google-spreadsheet` - For spreadsheet access
- `google-auth-library` - For JWT auth

### 10 Data Tabs:**

| Tab | Fields |
|-----|--------|
| Leads Master | Lead_ID, Date_Added, Platform, Username, Display_Name, Profile_URL, Followers_Count, Bio, Location, Business_Type, Product_Category, Lead_Source, Discovery_Method, Discovery_Source, Observed_Social_Signal, Recent_Activity_Confirmed, ICP_Score, ICP_Tier, Urgency_Flag, Messaging_Angle, Personalization_Hook, Conversation_Status, CRM_Status |
| Prospect Discovery Map | Lead_ID, Discovery_Method, Discovery_Source, Observed_Social_Signal, Recent_Activity_Confirmed, Research_Notes |
| Message Log | Message_ID, Lead_ID, Platform, Message_Type, Hook_Type, Personalization_Element, Message_Text, Date_Created, Approval_Status |
| Follow-Up Log | Lead_ID, Initial_Message_Date, Next_Action_Date, Followup_1_Date, Followup_2_Date, Followup_Status |
| DM Intelligence Library | Hook_ID, Hook_Type, Message_Template, Platform, Target_Audience, Reply_Rate, Conversion_Rate, Performance_Rating |
| Conversation Notes | Lead_ID, Platform, ICP_Persona, Interest_Level, Emotional_Tone, Pain_Point_Identified, Notes_For_Jill, Notes_For_Sandra |
| Campaign Metrics | (Weekly performance data) |
| System Activity Log | (All agent actions with timestamps) |
| AGENT_QUEUE | Task_Type, Assigned_To, Lead_ID, Status, Priority, Due_By, Notes |
| SETTINGS | Setting_Name, Setting_Value |

---

## Important Lessons

### March 24, 2026 — Duplicate Prevention

**CRITICAL rule added to Tom's SKILL.md:**
- MUST check for duplicate Lead_ID before adding to sheet
- MUST check for duplicate Username/Profile_URL (same account, different ID)
- If duplicate found, SKIP and report in session summary
- This is non-negotiable

### Dedupe Agent Created

- Created /root/.openclaw/workspace/skills/dedupe-agent/SKILL.md
- Can be invoked for future deduplications
- Uses dustid-sheets.js helper (getSheetRows, clearSheet, appendRow)

### March 24, 2026 — Dedupe SUCCESS!

**Method that worked:** Browser automation
- Opened Google Sheet via browser tool
- Used Data > Remove duplicates menu
- Selected only Column A (Lead_ID) to check
- Result: 405 duplicates removed, 70 unique rows remain

**Key insight:** Sub-agents kept timing out on exec commands. Browser automation bypassed this completely.

**Critical lesson learned:** Tom's prospecting criteria MUST be followed strictly. Do not add leads without proper verification.

**Tom's STRICT rules:**
1. Verify engagement spike is happening NOW (0-72 hours)
2. Confirm UK/Ireland location - don't assume
3. Find DM-overwhelmed signals in content
4. Time-stamp every lead with urgency tier (CRITICAL/HOT/WARM/EXPIRED)
5. Check for TikTok Shop presence
6. Test website checkout capability

**If TikTok search fails:**
- Try TikTok Creative Center (ads.tiktok.com/business/creativecenter)
- If BOTH fail → Report findings immediately to Audrey

---

## March 22, 2026 — Campaign Setup Complete

All 9 Dustid agent SOUL & SKILL files updated from Ken's combined documents. Full workflow stored in `memory/dustid-campaign-workflow.md`. Ready to run.

**Key Updates:**
- Tom prospects 100-150 leads per session (was 10-20)
- New criteria: 10-day trending, no website, DM-overwhelmed signals, UK+Ireland
- All agents have Google Sheet tab access defined
- 60-day free trial + 48-hour store build offer

---

## April 17, 2026 — Pipeline Improvements

### Tom's Skill Updated (Data Collection Fix)
**Problem:** 18 Instagram leads stuck because Followers_Count + Bio data was missing

**Solution:** Updated `/skills/smtl-scout/SKILL.md` with:
- **Required Fields Checklist** — Must capture: username, display_name, bio, followers_count, following_count, location, product_focus, recent_posts
- **Xpoz Workflow** — Use `getInstagramUser` after `getInstagramUsersByKeywords` to get FULL profile data
- **Data Quality Rules** — NO BLANK FIELDS. If you can't get followers + bio, don't add the lead.
- **Handling Missing Data** — Use browser automation as fallback, skip leads that can't be enriched

### Tyler's CRM Skill Created
**New File:** `/skills/smtl-crm-manager/SKILL.md`
- EngageBay API integration documented
- Contact creation workflow from Google Sheet → CRM
- Data mapping: Sheet fields → EngageBay contact fields
- Duplicate prevention rules
- Error handling and retry logic

**New Helper:** `/skills/engagebay-helper.js`
- `createContact()` — Create contact in EngageBay
- `getContactByEmail()` — Check for existing contacts
- `searchContacts()` — Find by username/lead_id
- `updateContact()` — Update existing contact
- `mapLeadToContact()` — Convert sheet row to EngageBay format

### Pipeline Status (April 17)
- **17 Draft Ready leads** — Ready for Tyler (CRM entry), all have complete copy from Sandra
- **19 leads scored by Elsie** — 3 PRIORITY, 13 HOT, 2 WARM, ready for Jill (Qualifier)
- **18 New leads diagnosed** — Stuck due to incomplete data (Tom to re-collect or archive)
- **1 duplicate found** — IG-021 = IG-016 (to be deleted)
- **5 malformed test leads** — Need cleanup

### Next Actions
1. Tom to verify `.env/engagebay.env` has valid API key
2. Tyler to process 17 Draft Ready leads into CRM
3. Archive or re-enrich the 18 stuck New leads
4. Delete duplicate IG-021 and test leads

---

_Update this file periodically with what's worth keeping long-term._
