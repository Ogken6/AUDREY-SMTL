# Pipeline Data Storage SOP

**Location:** `leads/`  
**Last Updated:** 2026-03-12

---

## Storage Strategy

| Format | Use For |
|--------|---------|
| **Markdown** | Agent outputs, pipeline stages, notes, drafts |
| **JSON** | Complex data, metrics, CRM entries, master index |

---

## Folder Structure

```
leads/
├── index.md              # Master overview + quick stats
├── PIPELINE_SOP.md       # ← You are here
├── prospecting.md        # Tom - Raw prospects
├── scoring.md            # Elsie - Scored leads (tables)
├── qualified.md         # Jill - Human-qualified leads
├── outreach/
│   ├── drafts/          # Pre-approval
│   └── sent.md          # Sandra - Sent messages
├── follow-up.md         # Kendy - Activities
├── crm.json             # Tyler - CRM entries
└── analytics.json       # Michelle - Metrics
```

---

## How to Request Data

### Quick Stats (JSON)
```bash
cat leads/index.json
```

### All Leads in Pipeline
```bash
cat leads/scoring.md
```

### Sent Outreach Messages
```bash
cat leads/outreach/sent.md
```

### CRM Entries
```bash
cat leads/crm.json
```

### Campaign Metrics
```bash
cat leads/analytics.json
```

---

## Pipeline Flow

1. **Tom** → `prospecting.md`
2. **Elsie** → `scoring.md`
3. **Jill** → `qualified.md`
4. **Sandra** → `outreach/sent.md`
5. **Kendy** → `follow-up.md`
6. **Tyler** → `crm.json`
7. **Michelle** → `analytics.json`

---

## Adding New Data

### Outreach (Sandra)
Add new entry to `outreach/sent.md`:
```markdown
## March 12, 2026

### @handle
**Platform:** Instagram | **Status:** Sent

> Your message here...
```

### Follow-Up (Kendy)
Add to `follow-up.md`:
```markdown
### March 12, 2026 - @handle
- Type: reminder
- Outcome: responded
- Notes: ...
```

### CRM (Tyler)
Add entry to `crm.json`:
```json
{
  "lead": "@handle",
  "stage": "outreach",
  "status": "active",
  "lastContact": "2026-03-12"
}
```

---

*This SOP lives in the leads folder. Always update relevant markdown/json file after each agent completes their work.*
