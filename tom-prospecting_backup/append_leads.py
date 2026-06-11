import json
import requests

SHEET_ID = "1bOR0HY_tg73-d6cjMpouN9jjY8meyl4ma1kCte3rqqg"
API_KEY = "AIzaSyALDFejLlxZM_4uEQwkDSPkVgkPBzY-UKo"

# Read new leads
with open("/root/.openclaw/workspace/tom-prospecting/new_leads.json", "r") as f:
    new_leads = json.load(f)

# Prepare rows for append
# Headers from existing sheet:
# Lead_ID, Date_Added, Platform, Username, Display_Name, Profile_URL, Followers_Count, Following_Count,
# Bio, Location, Business_Type, Product_Category, Lead_Source, ICP_Score, ICP_Tier, Messaging_Angle,
# Personalization_Hook, Conversation_Status, CRM_Status, Conversation_Summary, Last_Updated,
# Discovery_Method, Discovery_Source, Observed_Social_Signal, Urgency_Flag, Recent_Activity_Confirmed

rows = []
for lead in new_leads:
    row = [
        lead.get("Lead_ID", ""),
        lead.get("Date_Added", ""),
        lead.get("Platform", ""),
        lead.get("Username", ""),
        lead.get("Display_Name", ""),
        lead.get("Profile_URL", ""),
        lead.get("Followers_Count", ""),
        lead.get("Following_Count", ""),
        lead.get("Bio", ""),
        lead.get("Location", ""),
        lead.get("Business_Type", ""),
        lead.get("Product_Category", ""),
        lead.get("Lead_Source", ""),
        lead.get("ICP_Score", ""),
        lead.get("ICP_Tier", ""),
        lead.get("Messaging_Angle", ""),
        lead.get("Personalization_Hook", ""),
        lead.get("Conversation_Status", ""),
        lead.get("CRM_Status", ""),
        lead.get("Conversation_Summary", ""),
        lead.get("Last_Updated", ""),
        lead.get("Discovery_Method", ""),
        lead.get("Discovery_Source", ""),
        lead.get("Observed_Social_Signal", ""),
        lead.get("Urgency_Flag", ""),
        lead.get("Recent_Activity_Confirmed", "")
    ]
    rows.append(row)

# Try to append using API key (likely to fail for write operations without proper auth)
url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/LEADS_MASTER:append"
params = {
    "valueInputOption": "USER_ENTERED",
    "insertDataOption": "INSERT_ROWS",
    "key": API_KEY
}
body = {
    "values": rows
}

try:
    response = requests.post(url, params=params, json=body, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
