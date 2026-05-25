import os
import logging
import urllib.request
import urllib.error
import json

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
LEAD_RECIPIENT = os.environ.get("LEAD_RECIPIENT")


def send_lead_email(lead: dict):
    """Send lead email via Resend API."""

    logger.info(f"Sending lead email for {lead.get('name')} to {LEAD_RECIPIENT}")

    subject = f"New Loan Lead — {lead.get('name', 'Unknown')} ({lead.get('state', 'Unknown')})"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a1a2e; padding: 24px; border-radius: 8px 8px 0 0;">
            <h2 style="color: #ffffff; margin: 0;">🎯 New Loan Application Lead</h2>
            <p style="color: #a0a0b0; margin: 4px 0 0;">Via Cairn Credit Telegram Bot</p>
        </div>
        <div style="background: #f9f9f9; padding: 24px; border: 1px solid #e0e0e0;">
            <h3 style="color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px;">Contact Details</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; color: #666; width: 140px;"><strong>Name</strong></td>
                    <td style="padding: 8px 0; color: #333;">{lead.get('name', 'N/A')}</td>
                </tr>
                <tr style="background: #f0f0f0;">
                    <td style="padding: 8px 4px; color: #666;"><strong>Email</strong></td>
                    <td style="padding: 8px 4px;"><a href="mailto:{lead.get('email', '')}">{lead.get('email', 'N/A')}</a></td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #666;"><strong>Phone</strong></td>
                    <td style="padding: 8px 0;"><a href="tel:{lead.get('phone', '')}">{lead.get('phone', 'N/A')}</a></td>
                </tr>
            </table>
            <h3 style="color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; margin-top: 24px;">Application Details</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; color: #666; width: 140px;"><strong>State</strong></td>
                    <td style="padding: 8px 0; color: #333;">{lead.get('state', 'N/A')}</td>
                </tr>
                <tr style="background: #f0f0f0;">
                    <td style="padding: 8px 4px; color: #666;"><strong>Loan Amount</strong></td>
                    <td style="padding: 8px 4px; color: #333;">${lead.get('amount', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #666;"><strong>Credit Score</strong></td>
                    <td style="padding: 8px 0; color: #333;">{lead.get('credit', 'N/A').title()}</td>
                </tr>
                <tr style="background: #f0f0f0;">
                    <td style="padding: 8px 4px; color: #666;"><strong>Income Status</strong></td>
                    <td style="padding: 8px 4px; color: #333;">{lead.get('income', 'N/A').title()}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #666;"><strong>Previously Declined</strong></td>
                    <td style="padding: 8px 0; color: #333;">{lead.get('declined', 'N/A').title()}</td>
                </tr>
            </table>
        </div>
        <div style="background: #1a1a2e; padding: 16px 24px; border-radius: 0 0 8px 8px;">
            <p style="color: #a0a0b0; margin: 0; font-size: 13px;">
                ⚡ Respond within 24 hours as promised to the applicant.
            </p>
        </div>
    </body>
    </html>
    """

    payload = json.dumps({
        "from": "Cairn Credit Bot <onboarding@resend.dev>",
        "to": [LEAD_RECIPIENT],
        "subject": subject,
        "html": html_body,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        logger.info(f"Email sent successfully: {result}")
        return result
