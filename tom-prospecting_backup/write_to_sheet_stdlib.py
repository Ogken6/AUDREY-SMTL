#!/usr/bin/env python3
"""Write leads to Google Sheet using only Python standard library."""

import json
import base64
import hashlib
import hmac
import time
import urllib.request
import urllib.parse
import ssl

# Disable SSL verification for this environment (not recommended for production)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

SHEET_ID = "1bOR0HY_tg73-d6cjMpouN9jjY8meyl4ma1kCte3rqqg"
RANGE = "LEADS_MASTER"

# Read service account credentials
with open("/root/.openclaw/workspace/tom-service-account.json", "r") as f:
    creds = json.load(f)

# Read new leads
with open("/root/.openclaw/workspace/tom-prospecting/new_leads.json", "r") as f:
    new_leads = json.load(f)

client_email = creds["client_email"]
private_key = creds["private_key"]
token_uri = creds["token_uri"]

# Create JWT
now = int(time.time())
claim = {
    "iss": client_email,
    "scope": "https://www.googleapis.com/auth/spreadsheets",
    "aud": token_uri,
    "exp": now + 3600,
    "iat": now
}

# Base64 URL-safe encoding without padding
def b64encode(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

header = b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}))
payload = b64encode(json.dumps(claim))

# Sign with RSA private key
message = f"{header}.{payload}"

# Parse PEM private key
import re
pem_lines = private_key.strip().split('\n')
key_data = ''.join([line for line in pem_lines if not line.startswith('-----')])
key_bytes = base64.b64decode(key_data)

# Simple ASN.1 parsing for RSA key
# For a proper implementation we'd need more parsing, but let's try a different approach
# Use subprocess to call openssl for signing
import subprocess

try:
    # Write JWT header.payload to temp file
    with open('/tmp/jwt_message.txt', 'w') as f:
        f.write(message)
    
    # Use openssl to sign with the private key
    proc = subprocess.run(
        ['openssl', 'dgst', '-sha256', '-sign', '/root/.openclaw/workspace/tom-service-account.json'],
        input=message.encode(),
        capture_output=True
    )
    
    if proc.returncode != 0:
        print(f"OpenSSL signing failed: {proc.stderr.decode()}")
        # Try alternative: use openssl with key file
        with open('/tmp/private_key.pem', 'w') as f:
            f.write(private_key)
        proc = subprocess.run(
            ['openssl', 'dgst', '-sha256', '-sign', '/tmp/private_key.pem'],
            input=message.encode(),
            capture_output=True
        )
        if proc.returncode != 0:
            print(f"Alternative signing also failed: {proc.stderr.decode()}")
            exit(1)
    
    signature = b64encode(proc.stdout)
    jwt = f"{message}.{signature}"
    
    # Exchange JWT for access token
    token_data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt
    }).encode()
    
    req = urllib.request.Request(
        token_uri,
        data=token_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
        token_response = json.loads(response.read().decode())
        access_token = token_response["access_token"]
        print(f"Got access token: {access_token[:20]}...")
    
    # Prepare rows
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
    
    # Append to sheet
    append_data = json.dumps({"values": rows}).encode()
    
    append_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{RANGE}:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS"
    
    req = urllib.request.Request(
        append_url,
        data=append_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )
    
    with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
        result = json.loads(response.read().decode())
        print(f"Success! Appended {len(rows)} rows")
        print(f"Updated range: {result.get('updates', {}).get('updatedRange', 'N/A')}")
        print(f"Rows added: {result.get('updates', {}).get('updatedRows', 'N/A')}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
