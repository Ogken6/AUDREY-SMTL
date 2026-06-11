# Dustid Mission Control Dashboard

A standalone, local web dashboard for managing Dustid sales campaigns with real-time Google Sheets integration, historical snapshots, and automated alerts.

## Features

### 📊 Real-Time Pipeline View
- Live metrics from your Google Sheet
- Pipeline stages: New → Scored → Qualified → Draft Ready → Messaged → Responded → Booked
- Lead cards with quick detail view
- Color-coded PRIORITY/HOT/WARM tiers

### 🚨 Smart Alerts
- PRIORITY leads waiting >2 hours without messages
- HOT leads stuck >1 day
- Qualified leads not in CRM
- Alerts sent via Telegram and email

### 👥 Team Status
- Agent workload overview (Tom, Elsie, Sandra, Jill, Kendy, Tyler)
- Real-time status indicators
- Queue counts per agent

### 📈 Report Generation
- **Daily Summary**: Pipeline activity, new leads, messages sent
- **Weekly Report**: Conversion rates, trends, team performance
- **Founder Report**: Executive summary for stakeholders
- **Full Export**: Complete data as JSON (PDF/Excel coming)

### 🔄 Historical Data
- Automatic snapshots every refresh
- 30-day trend tracking
- Compare current vs. previous periods
- Works offline with cached data

### 🏢 Multi-Campaign Support
- Switch between campaigns (Social Sellers, Dustid Ecommerce, etc.)
- Each campaign uses separate Google Sheets
- Easy campaign add/remove

## Setup

### 1. Open the Dashboard
Simply open `index.html` in your web browser:
```bash
# On macOS
open index.html

# On Linux
xdg-open index.html

# On Windows
start index.html
```

Or drag and drop `index.html` into your browser.

### 2. Configure Google Sheets (First Time Only)

1. Click **⚙ Settings** in the top right
2. Verify your Sheet ID and API Key are correct:
   - **Sheet ID**: `1bOR0HY_tg73-d6cjMpouN9jjY8meyl4ma1kCte3rqqg`
   - **API Key**: `AIzaSyALDFejLlxZM_4uEQwkDSPkVgkPBzY-UKo`
3. Click **Save Settings**

### 3. Configure Alerts (Optional but Recommended)

#### Telegram Alerts:
1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Copy your bot token
3. Get your chat ID (message @userinfobot)
4. Enter both in Settings

#### Email Alerts:
- Currently logs to console
- For real email alerts, integrate with:
  - SendGrid
  - Mailgun
  - AWS SES
  - Or your preferred email service

### 4. Refresh Data

Click **↻ Refresh** or wait for auto-refresh (default: every 15 minutes).

## Dashboard Sections

### Header
- **Last Updated**: Shows when data was last fetched
- **Refresh**: Manual data refresh
- **Settings**: Configure connections and preferences

### Campaign Selector
Switch between active campaigns. Currently configured:
- Social Sellers Campaign (active)
- Dustid Ecommerce (placeholder)

### Metrics Grid
Key numbers at a glance:
- **Total Leads**: All leads in pipeline
- **PRIORITY**: Immediate action required
- **Messages Sent**: Outreach progress
- **Response Rate**: Conversion metric
- **Consultations Booked**: End goal

### Alerts Section
Urgent items requiring attention:
- 🚨 **Urgent**: PRIORITY leads waiting too long
- ⚠️ **Warning**: HOT leads delayed
- ℹ️ **Info**: Qualified leads ready for CRM

### Pipeline Overview
Visual Kanban-style board showing leads at each stage. Click any lead card to see full details.

### Team Status
Agent workload and availability:
- Green dot = Active
- Yellow dot = Idle
- Gray dot = Offline

### Report Generation
Export data in multiple formats:
- Daily/Weekly/Founder reports as JSON
- Full data export for analysis

## Data Flow

```
Google Sheets → Dashboard → Local Storage (Snapshots)
                     ↓
              Telegram/Email Alerts
```

## File Structure

```
dustid-dashboard/
├── index.html          # Main dashboard (single file)
├── README.md           # This file
└── snapshots/          # Historical data (auto-created)
```

## Customization

### Change Refresh Interval
Settings → Auto-refresh interval → Select time (5/15/30/60 minutes)

### Add New Campaign
1. Create a new Google Sheet
2. Share it with your service account
3. Click **+ Add Campaign** in the dashboard
4. Enter the new Sheet ID

### Modify Alert Rules
Edit the `generateAlerts()` function in `index.html`:

```javascript
// Add custom alert logic
if (yourCondition) {
    alerts.push({
        type: 'urgent', // or 'warning', 'info'
        title: 'Your Alert Title',
        message: 'Your alert message',
        lead: lead
    });
}
```

## Troubleshooting

### "Update failed" Message
1. Check internet connection
2. Verify Sheet ID and API Key in Settings
3. Make sure Google Sheet is publicly readable (or shared with API key)
4. Check browser console for errors (F12 → Console)

### Dashboard Shows Cached Data
- Dashboard automatically falls back to cached data if fetch fails
- Click **Refresh** to try again
- Check Settings for correct credentials

### Alerts Not Sending
- Verify Telegram bot token and chat ID
- Check that bot has permission to send messages
- For email: currently requires backend integration

### Data Looks Wrong
- Check that sheet columns match expected headers
- Verify row data is in correct columns
- Dashboard expects: Lead_ID, Platform, Username, etc.

## Future Enhancements (v2)

- [ ] Drag-and-drop lead cards between stages
- [ ] PDF report generation with charts
- [ ] Excel export (.xlsx)
- [ ] Dark/light theme toggle
- [ ] Mobile app wrapper
- [ ] Real-time WebSocket updates
- [ ] Advanced filtering and search
- [ ] Team member login/access control

## Security Notes

- API Key is stored in browser localStorage
- No data leaves your machine except:
  - Google Sheets API calls (read-only)
  - Telegram/email alerts (if configured)
- Keep your `index.html` file secure
- Don't commit API keys to version control

## Support

For issues or feature requests, contact Audrey (SMTL Team Lead) or update this README with solutions you discover.

---

**Built for Dustid by Audrey and Team**  
*Making sales operations visible and actionable*
