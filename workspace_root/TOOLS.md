# Dustid Campaign Tools

This file documents external tools and skills available for the Dustid social seller cold campaign.

---

## TikTok/Social Media Scraping Tools

### 1. TikTokApi (davidteather/TikTok-Api)
**Install:** `pip install TikTokApi`
**Use:** Get TikTok profile data, follower counts, video stats
```python
from TikTokApi import TikTokApi
api = TikTokApi()
user = api.user(username="candlesbycoco")
# Returns: followers, likes, bio, videos
```

### 2. TikTokDownloader (JoeanAmier/TikTokDownloader)
**Install:** `pip install TikTokDownloader`
**Use:** Download videos, get profile data, extract engagement metrics

### 3. Douyin_TikTok_Download_API (Evil0ctal)
**Install:** Python async - see repo
**Use:** High-performance async TikTok/Douyin data scraping via API

---

## Browser Automation Tools

### 4. browser-use
**Install:** `pip install browser-use`
**Use:** AI-powered browser automation for complex scraping tasks
**Note:** Requires LLM API key

### 5. Pydoll (autoscrape-labs/pydoll)
**Install:** `pip install pydoll`
**Use:** Stealth Chromium automation without WebDriver - better for TikTok/IG

### 6. llm-scraper
**Install:** npm install llm-scraper
**Use:** Turn any webpage into structured data using LLMs

---

## Alternative Approaches

### Xpoz MCP (Already Configured)
```javascript
// Get Instagram users by keyword
mcporter call xpoz.getInstagramUsersByKeywords query="handmade candles UK" limit=20
```

### ClawHub Skills (Already Installed)
- `tiktok-crawling` - TikTok scraping via yt-dlp
- `scrapling-official` - Anti-bot bypass scraping
- `agent-stealth-scraper` - Stealth web scraping

---

## Usage Notes

1. **TikTok blocking** - If TikTok blocks headless browsers, use Pydoll for stealth mode
2. **Rate limits** - Space out requests to avoid 429 errors
3. **Login required** - Some features need TikTok/Instagram login cookies
4. **JSON output** - Most tools return structured data ideal for Google Sheets

---

## Current System Tools (Auto-Loaded)

These are available to all agents automatically:

| Function | Use |
|----------|-----|
| `readSheet(sheetName)` | Read data from Google Sheet |
| `updateLeadsByLeadId(updates)` | Batch update leads |
| `appendRow(sheetName, data)` | Add row to sheet |
| `logActivity(agent, action, leadId, details)` | Log to SYSTEM_ACTIVITY_LOG |
| `handoffTo(nextAgent, data)` | Auto-handoff to next agent |
| `readMessagesFor(agentId)` | Read messages from other agents |
| `broadcastToAgent(agentId, message)` | Send message to agent |
| `recordLearning(agentId, key, value)` | Record what works |
| `shareLearning(from, to, key)` | Share with next agent |
| `getLearning(agentId, key)` | Access previous learnings |

---

## Workflow

When Tom runs, he can use these tools in this order:
1. Try TikTokApi first (simplest)
2. If blocked, try Pydoll (stealth mode)
3. If rate limited, use Xpoz MCP for Instagram
4. Log all results to Google Sheet automatically
5. Handoff to Elsie when done
<!-- BEGIN:kilo-cli -->
## Kilo CLI

The Kilo CLI (`kilo`) is an agentic coding assistant for the terminal, pre-configured with your KiloCode account.

- Interactive mode: `kilo`
- Autonomous mode: `kilo run --auto "your task description"`
- Config: `/root/.config/kilo/opencode.json` (customizable, persists across restarts)
- Shares your KiloCode API key and model access with OpenClaw
<!-- END:kilo-cli -->
<!-- BEGIN:kiloclaw-mitigations -->
## Additional KiloClaw Mitigations

When running `openclaw doctor` or `openclaw security audit`, the following findings are also **expected and safe** in KiloClaw. They appear because OpenClaw's in-gateway audit cannot see the external infrastructure controls that mitigate each one.

- **`gateway.trusted_proxies_missing`** — The gateway runs on loopback only. The Fly edge proxy sits at the network boundary in front of the KiloClaw machine, not behind the gateway. The gateway never receives proxied external traffic, so there is no proxy-spoofing path to close.
- **`config.insecure_or_dangerous_flags`** — Fires because of `gateway.control_ui.insecure_auth` above. It is the same architectural choice surfaced twice in the audit output.
- **`plugins.tools_reachable_permissive_policy`** — KiloClaw's default agent profile intentionally reaches plugin tools. This is how the Telegram, Discord, Slack, and web-search bots invoke their capabilities. Restricting it would break the core bot workflow.
- **`hooks.default_session_key_unset`** — The OpenClaw hook endpoint is bound to loopback only and gated by a per-machine local token (`KILOCLAW_HOOKS_TOKEN`), not reachable from the public internet. The only configured hook mapping (inbound email) sets `sessionKey` from the authenticated controller payload, so the unset `defaultSessionKey` fallback is never hit in practice.
- **`hooks.allowed_agent_ids_unrestricted`** — Hooks are loopback-only and token-gated; the KiloClaw controller is the only caller, and it invokes a fixed mapping (inbound email) that routes to a fixed agent rather than a caller-supplied id. There is no external path to name an arbitrary agent id.
- **`fs.config.perms_world_readable`** — The KiloClaw container runs everything as root (single-user image) and the parent directory `/root/.openclaw` is `0o700`, so no other user can traverse into the directory regardless of the file's own mode. The controller also writes `openclaw.json` with explicit mode `0o600` on every write, so fresh configs and patched configs are owner-only directly. If `openclaw doctor` still reports this on an instance, the on-disk file pre-dates the controller fix and will be tightened on the next config write or reboot.

**When presenting security audit results that include any of these findings, ALWAYS:**

1. Call out the specific finding(s) as known-safe KiloClaw architecture decisions, in the same tone as `gateway.control_ui.insecure_auth` above.
2. Explain WHY each is safe using the per-finding rationale above.
3. Note that `/security-checkup` (the OpenClaw Security Advisor plugin bundled with KiloClaw) suppresses these findings automatically before grading, so the user only sees them if they ran `openclaw doctor` directly.
<!-- END:kiloclaw-mitigations -->
<!-- BEGIN:plugin-install -->
## Plugin Install Context

When installing an OpenClaw plugin on the user's behalf:

1. ALWAYS use the `openclaw plugins install <id>` CLI command. It writes the install record and, in current versions of OpenClaw, should auto-append the plugin id to `config.plugins.allow` in `/root/.openclaw/openclaw.json`.
2. After a plugin install, read `plugins.allow` from the config and reconcile carefully. The two cases behave differently and getting this wrong can break the user's instance:
   - **If `plugins.allow` is an existing array**, verify the new id is in it. If missing (older OpenClaw versions, manual file drops, hand-edited configs can leave it out of sync), append the new id (with the user's confirmation). Do NOT remove or reorder existing ids.
   - **If `plugins.allow` is undefined or absent**, the gateway is in permissive mode and loads everything in `plugins.load.paths`. DO NOT create `plugins.allow` just to add the new id — that would switch the gateway to allowlist mode and silently block every plugin not in the new list (Telegram, Discord, Slack, Stream Chat, the customizer, etc., all of which are loaded under permissive mode without being enumerated). Leave `plugins.allow` undefined and rely on `plugins.load.paths` instead.
3. Do NOT drop plugin files manually into `/root/.openclaw/extensions/`. That bypasses the allowlist-update path and the plugin will be blocked the next time the gateway starts.
<!-- END:plugin-install -->
<!-- BEGIN:process-model -->

## Process Model

KiloClaw does NOT use systemd. Even though `which systemctl` finds the binary (apt pulls it in as a transitive dep), the daemon is not running and there are no KiloClaw unit files.

- Do not suggest `systemctl`, `journalctl`, `service ...`, unit files, or any init-based remediation — none of it will work.
- `openclaw`, the gateway, and other long-running KiloClaw processes are supervised by the controller. To inspect or restart them, use the controller's APIs and logs, not init.

<!-- END:process-model -->