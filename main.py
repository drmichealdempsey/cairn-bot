import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from bot import setup_handlers
from email_sender import send_lead_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = FastAPI()
ptb_app = Application.builder().token(BOT_TOKEN).build()
setup_handlers(ptb_app)


@app.on_event("startup")
async def startup():
    await ptb_app.initialize()
    await ptb_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    logger.info(f"Webhook set to {WEBHOOK_URL}/webhook")


@app.on_event("shutdown")
async def shutdown():
    await ptb_app.shutdown()


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)
    await ptb_app.process_update(update)
    return {"ok": True}


@app.get("/")
async def root():
    return {"status": "Cairn Credit Bot is running ✅"}


@app.get("/test-email")
async def test_email():
    """Hit this URL to test if email is working."""
    try:
        send_lead_email({
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1 555 000 0000",
            "state": "Texas",
            "amount": "1000-2500",
            "credit": "poor",
            "income": "yes",
            "declined": "yes",
        })
        return {"status": "✅ Email sent successfully! Check your inbox."}
    except Exception as e:
        return {"status": "❌ Email failed", "error": str(e)}
