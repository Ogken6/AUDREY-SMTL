import urllib.request
import json
import os

os.makedirs('/root/.openclaw/workspace/tom-prospecting', exist_ok=True)

url = "https://sheets.googleapis.com/v4/spreadsheets/1bOR0HY_tg73-d6cjMpouN9jjY8meyl4ma1kCte3rqqg/values/LEADS_MASTER?key=AIzaSyALDFejLlxZM_4uEQwkDSPkVgkPBzY-UKo&fields=values"

try:
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    rows = data.get('values', [])
    print(f"Total rows: {len(rows)}")
    
    # Extract existing usernames for deduplication
    existing_usernames = set()
    for i, row in enumerate(rows[1:], 1):  # skip header
        if len(row) > 3:
            existing_usernames.add(row[3].strip().lower())
    
    print(f"Existing usernames: {len(existing_usernames)}")
    
    # Save to file
    with open('/root/.openclaw/workspace/tom-prospecting/existing_usernames.json', 'w') as f:
        json.dump(sorted(list(existing_usernames)), f)
    
    # Also save all rows for reference
    with open('/root/.openclaw/workspace/tom-prospecting/existing_leads.json', 'w') as f:
        json.dump(rows, f)
        
    print("Done")
except Exception as e:
    print(f"Error: {e}")
