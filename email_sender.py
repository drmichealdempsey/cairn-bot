import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
LEAD_RECIPIENT = os.environ.get("LEAD_RECIPIENT")


def send_lead_email(lead: dict):
    """Send a formatted lead email to Cairn Credit team."""

    logger.info(f"Attempting to send lead email for {lead.get('name')} to {LEAD_RECIPIENT}")
    logger.info(f"From Gmail: {GMAIL_ADDRESS}")

    subject = f"🎯 New Loan Lead — {lead.get('name', 'Unknown')} ({lead.get('state', 'Unknown')})"

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
                    <td style="padding: 8px 4px; color: #333;"><a href="mailto:{lead.get('email', '')}">{lead.get('email', 'N/A')}</a></td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #666;"><strong>Phone</strong></td>
                    <td style="padding: 8px 0; color: #333;"><a href="tel:{lead.get('phone', '')}">{lead.get('phone', 'N/A')}</a></td>
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

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = LEAD_RECIPIENT
    msg.attach(MIMEText(html_body, "html"))

    logger.info("Connecting to Gmail SMTP...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, LEAD_RECIPIENT, msg.as_string())
    logger.info(f"Lead email sent successfully to {LEAD_RECIPIENT}")
