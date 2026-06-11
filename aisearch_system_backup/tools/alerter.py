#!/usr/bin/env python3
"""
alerter.py — Alert dispatcher for SENTINEL
Routes alerts to Slack, email, SMS, and Telegram based on severity level.
Telegram is the primary real-time channel for CRITICAL alerts.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# CRITICAL → Telegram (instant push), ERROR/WARNING → Slack digest, INFO → daily digest
CHANNEL_ROUTING = {
    "INFO":     ["slack_digest"],
    "WARNING":  ["slack"],
    "ERROR":    ["slack", "telegram"],
    "CRITICAL": ["telegram", "slack"],
}

class Alerter:
    """
    Dispatches alerts to configured channels: Slack, email, SMS, Telegram.
    Telegram is the primary real-time channel for all severity levels.
    """

    def __init__(
        self,
        slack_webhook: Optional[str] = None,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        email_config: Optional[dict] = None,
        sms_config: Optional[dict] = None,
    ):
        self.slack_webhook = slack_webhook or os.environ.get("SLACK_WEBHOOK_URL")
        self.telegram_bot_token = telegram_bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = telegram_chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        self.email_config = email_config or self._email_config_from_env()
        self.sms_config = sms_config or self._sms_config_from_env()

    def send(
        self,
        severity: str,
        title: str,
        body: str,
        agent: Optional[str] = None,
        run_id: Optional[str] = None,
        recovery_ref: Optional[str] = None,
    ) -> dict:
        """
        Send an alert to all channels appropriate for its severity.
        Returns dict with per-channel status.
        """
        channels = CHANNEL_ROUTING.get(severity, ["telegram"])
        results = {}

        for channel in channels:
            if channel == "slack":
                results["slack"] = self._send_slack(severity, title, body)
            elif channel == "slack_digest":
                results["slack_digest"] = self._send_slack_digest(title, body)
            elif channel == "email":
                results["email"] = self._send_email(title, body)
            elif channel == "sms":
                results["sms"] = self._send_sms(title, body)
            elif channel == "telegram":
                results["telegram"] = self._send_telegram(severity, title, body, agent, run_id, recovery_ref)

        self._log_to_file(severity, title, body, agent, run_id, recovery_ref)
        logger.info(f"Alert sent [{severity}]: {title}")
        return results

    def _send_telegram(
        self,
        severity: str,
        title: str,
        body: str,
        agent: Optional[str] = None,
        run_id: Optional[str] = None,
        recovery_ref: Optional[str] = None,
    ) -> dict:
        """
        Send alert to Telegram channel.
        Uses the Bot API sendMessage endpoint — no library required.
        """
        import requests
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return {"status": "skipped", "reason": "telegram not configured"}

        # Emoji per severity
        emoji = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "🔴",
            "CRITICAL": "🚨",
        }.get(severity, "📋")

        # Build the message — MarkdownV2 format for clean rendering in Telegram
        # Escape special MarkdownV2 characters in body
        def escMD2(text):
            # Escape: .!()-[]{}#*+/?=~|^>_`\
            import re
            for ch in r'.\!()-[]{}#*+/?=~|^>_`':
                text = text.replace(ch, '\\' + ch)
            return text

        # Alert header
        header = f"*{emoji} ORACLE ALERT [{severity}]*\n"
        header += f"*{escMD2(title)}*\n\n"
        header += f"{escMD2(body)}\n\n"

        details = []
        if agent:
            details.append(f"Agent: `{agent}`")
        if run_id:
            details.append(f"Run: `{run_id}`")
        if recovery_ref:
            details.append(f"Recovery: {recovery_ref}")

        if details:
            header += " | ".join(details)

        payload = {
            "chat_id": self.telegram_chat_id,
            "text": header,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": "true",
        }

        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            resp = requests.post(url, json=payload, timeout=15)
            data = resp.json()

            if data.get("ok"):
                return {"status": "SUCCESS", "message_id": data.get("result", {}).get("message_id")}
            else:
                return {"status": "ERROR", "telegram_error": data.get("description", "unknown")}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def _send_slack(self, severity: str, title: str, body: str) -> dict:
        """Send Slack alert."""
        import requests
        if not self.slack_webhook:
            return {"status": "skipped", "reason": "no webhook configured"}
        emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "🔴", "CRITICAL": "🚨"}.get(severity, "📋")
        color = {"INFO": "#36a64f", "WARNING": "#ff9900", "ERROR": "#dc3545",
                 "CRITICAL": "#dc3545"}.get(severity, "#36a64f")
        payload = {
            "text": f"{emoji} *{title}*",
            "attachments": [{"text": body, "color": color}]
        }
        try:
            resp = requests.post(self.slack_webhook, json=payload, timeout=10)
            return {"status": "SUCCESS" if resp.ok else "ERROR", "response": resp.text[:100]}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def _send_slack_digest(self, title: str, body: str) -> dict:
        """Send daily digest to Slack (INFO only)."""
        return self._send_slack("INFO", title, body)

    def _send_email(self, title: str, body: str) -> dict:
        """Send email alert via SMTP."""
        if not self.email_config:
            return {"status": "skipped", "reason": "no email config"}
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body)
        msg["Subject"] = f"[ORACLE] {title}"
        msg["From"] = self.email_config.get("from")
        msg["To"] = self.email_config.get("to")
        try:
            with smtplib.SMTP(self.email_config["host"], self.email_config.get("port", 587)) as server:
                if self.email_config.get("tls"):
                    server.starttls()
                server.login(self.email_config["user"], self.email_config["pass"])
                server.send_message(msg)
            return {"status": "SUCCESS"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def _send_sms(self, title: str, body: str) -> dict:
        """Send SMS alert via Twilio."""
        if not self.sms_config:
            return {"status": "skipped", "reason": "no SMS config"}
        try:
            from twilio.rest import Client
            client = Client(self.sms_config["sid"], self.sms_config["token"])
            client.messages.create(
                body=f"ORACLE [{title}]: {body[:160]}",
                from_=self.sms_config["from"],
                to=self.sms_config["to"],
            )
            return {"status": "SUCCESS"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def _log_to_file(
        self,
        severity: str,
        title: str,
        body: str,
        agent: Optional[str],
        run_id: Optional[str],
        recovery_ref: Optional[str],
    ):
        """Append alert to sentinel_alerts.jsonl (append-only log)."""
        import json
        from datetime import datetime
        alert_id = f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        record = {
            "alert_id": alert_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": severity,
            "description": title,
            "body": body,
            "agent": agent,
            "run_id": run_id,
            "recovery_ref": recovery_ref,
        }
        log_path = "/root/.openclaw/workspace/aisearch_system/memory/sentinel_alerts.jsonl"
        with open(log_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def _email_config_from_env(self) -> dict:
        host = os.environ.get("SMTP_HOST")
        if not host:
            return {}
        return {
            "host": host,
            "port": int(os.environ.get("SMTP_PORT", "587")),
            "user": os.environ.get("SMTP_USER"),
            "pass": os.environ.get("SMTP_PASS"),
            "from": os.environ.get("ALERT_EMAIL_FROM"),
            "to": os.environ.get("ALERT_EMAIL_TO"),
            "tls": True,
        }

    def _sms_config_from_env(self) -> dict:
        sid = os.environ.get("TWILIO_ACCOUNT_SID")
        if not sid:
            return {}
        return {
            "sid": sid,
            "token": os.environ.get("TWILIO_AUTH_TOKEN"),
            "from": os.environ.get("TWILIO_FROM"),
            "to": os.environ.get("ALERT_SMS_TO"),
        }