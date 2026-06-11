# TOOLS.md — Phil's Tools

## Operational Stack (Planned / Not Yet Connected)

### Scraping & Monitoring
| Tool | Status | Notes |
|------|--------|-------|
| Apify (Reddit, X, FB scrapers) | Not connected | Recommended for production |
| Firecrawl | Not connected | For website/event listing scraping |
| Google Alerts | Setup pending | Free signal layer |
| web_search (OpenClaw) | Available | Basic monitoring capability |
| web_fetch (OpenClaw) | Available | Light page content extraction |
| browser | Available | Full scraping when needed |

### Communication
| Tool | Status | Notes |
|------|--------|-------|
| WhatsApp Business API (via 360dialog/Twilio) | Not connected | Meta-approved templates required |
| Telegram Bot | Not connected | Simpler fallback option |
| message (OpenClaw) | Partial | Can send to channels if configured |

### Flight Monitoring
| Tool | Status | Notes |
|------|--------|-------|
| AviationStack API | Not connected | Free tier: 500 req/month |
| AeroDataBox | Not connected | Better JKIA coverage, paid |
| FlightAware AeroAPI | Not connected | Most reliable, paid |

### Database / CRM
| Tool | Status | Notes |
|------|--------|-------|
| Airtable | Not connected | Recommended for non-technical use |
| Supabase | Not connected | Recommended for SQL queries |
| Local CSV/JSON | Available | Temporary holding until CRM integrated |

### Automation
| Tool | Status | Notes |
|------|--------|-------|
| n8n (self-hosted) | Not connected | Recommended workflow automation |
| Make.com | Not connected | Cloud alternative |
| Zapier | Not connected | Simplest setup |

## Workflow Automation Recommendations

**Recommended path:** Set up n8n self-hosted for the full pipeline. It handles:
- Scheduled scraping triggers
- API calls to flight data providers
- Lead scoring calculations
- Message formatting and dispatch
- CRM updates
- Morning digest generation

**Quick start path:** Use OpenClaw cron + exec for initial version while infrastructure is being built.

## Keyword Sources File

Primary keywords live in: `config/keywords.md`
Scraping targets listed in: `scraping/sources.md`

## Reference Documents

- Full system spec: Referenced from conversation history (Transport Intent Radar v2 README)
- Lead classifier: `prompts/lead_classifier.md`
- Message generator: `prompts/message_generator.md`
- Follow-up sequence: `prompts/follow_up_sequence.md`
- Lead scoring: `scoring/lead_scoring.md`
- Fleet schema: `fleet/availability_schema.md`
- CRM schema: `crm/lead_schema.md`
- Morning digest template: `alerts/morning_digest.md`
- Seasonal calendar: `workflows/seasonal_calendar.md`
- Partnership strategy: `docs/partnership_strategy.md`
- Future features: `docs/future_features.md`
- Compliance: `docs/compliance.md`

---

*Phil's workspace. All transport intelligence runs through here.*
