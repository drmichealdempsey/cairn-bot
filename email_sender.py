import os
import logging
import urllib.request
import json

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")


def send_lead_notification(lead: dict):
    """Send lead details to admin via Telegram message."""

    message = (
        f"🎯 *New Loan Lead!*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Name:* {lead.get('name', 'N/A')}\n"
        f"📧 *Email:* {lead.get('email', 'N/A')}\n"
        f"📞 *Phone:* {lead.get('phone', 'N/A')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 *State:* {lead.get('state', 'N/A')}\n"
        f"💰 *Amount:* ${lead.get('amount', 'N/A')}\n"
        f"📊 *Credit:* {lead.get('credit', 'N/A').title()}\n"
        f"💼 *Income:* {lead.get('income', 'N/A').title()}\n"
        f"🏦 *Declined Before:* {lead.get('declined', 'N/A').title()}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ Respond within 24 hours!"
    )

    payload = json.dumps({
        "chat_id": ADMIN_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        logger.info(f"Lead notification sent: {result}")
        return result


# Keep this name so bot.py doesn't need changes
def send_lead_email(lead: dict):
    return send_lead_notification(lead)
