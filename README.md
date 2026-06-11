# KENOC - KiloClaw Instance Backup

**Created:** 2026-06-11
**Owner:** Ogken6

## What's Backed Up

This repo contains a full snapshot of the KiloClaw agent workspace including:

- **10 Dustid Sales & Marketing Agents** (Tom, Elsie, Jill, Sandra, Kendy, Michelle, Samira, Tyler, Nate, Claire)
- **Content & SEO Agents** (Ryan, Wayne, OB1-OB6)
- **GTO/GTM Agents** (Fabio, Elena, Raj, Livy, Marcus)
- **All skill files, SOUL files, and scripts**
- **Google Sheets integration helpers**
- **EngageBay CRM integration**
- **Campaign data and pipeline outputs**
- **Memory files and agent configurations**

## Structure

```
├── skills/          # All agent skill definitions
├── agents/          # Agent soul and config files
├── memory/          # Session memory and daily logs
├── smtl-team/       # Dustid campaign team files
├── fabio/           # GTM chief of staff
├── ryan/            # Content & growth officer
├── wayne/           # SEO expert
└── [scripts]        # Utility scripts (Node.js, Python, Shell)
```

## Restore

To restore on another KiloClaw instance:
```bash
git clone https://github.com/Ogken6/KENOC.git ~/.openclaw/workspace
```

---
*Auto-generated backup - KiloClaw 🦾*