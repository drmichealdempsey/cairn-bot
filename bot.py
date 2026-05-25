import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from email_sender import send_lead_email

logger = logging.getLogger(__name__)

# ── Conversation states ──────────────────────────────────────────────────────
(
    STATE_MENU,
    STATE_STATE,
    STATE_AMOUNT,
    STATE_CREDIT,
    STATE_INCOME,
    STATE_DECLINED,
    STATE_NAME,
    STATE_EMAIL,
    STATE_PHONE,
    STATE_DONE,
) = range(10)

# ── Helpers ──────────────────────────────────────────────────────────────────

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Check My Eligibility", callback_data="start_quiz")],
        [InlineKeyboardButton("ℹ️ Learn More", callback_data="learn_more")],
    ])


def us_states():
    """Return quick-pick state buttons (common US states)."""
    states = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California",
        "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
        "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
        "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
        "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
        "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
        "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
        "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
        "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
        "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
    ]
    # Build rows of 2
    buttons = []
    for i in range(0, len(states), 2):
        row = [InlineKeyboardButton(states[i], callback_data=f"state_{states[i]}")]
        if i + 1 < len(states):
            row.append(InlineKeyboardButton(states[i + 1], callback_data=f"state_{states[i+1]}"))
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


def amount_keyboard():
    amounts = [
        ("$500 – $1,000", "500-1000"),
        ("$1,000 – $2,500", "1000-2500"),
        ("$2,500 – $5,000", "2500-5000"),
        ("$5,000 – $10,000", "5000-10000"),
        ("$10,000+", "10000+"),
    ]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=f"amount_{val}")]
        for label, val in amounts
    ])


def credit_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Poor (below 580)", callback_data="credit_poor")],
        [InlineKeyboardButton("⚠️ Fair (580–669)", callback_data="credit_fair")],
        [InlineKeyboardButton("🤷 Not Sure", callback_data="credit_unknown")],
    ])


def income_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes — employed / regular income", callback_data="income_yes")],
        [InlineKeyboardButton("🔄 Self-employed / freelance", callback_data="income_self")],
        [InlineKeyboardButton("❌ No income currently", callback_data="income_no")],
    ])


def declined_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, I've been declined", callback_data="declined_yes")],
        [InlineKeyboardButton("🆕 No, first time applying", callback_data="declined_no")],
    ])


# ── Handlers ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 *Welcome to Cairn Credit!*\n\n"
        "We help people with low or damaged credit scores get a fair loan review — "
        "even if traditional banks have turned you down.\n\n"
        "✅ Real humans review every application\n"
        "⚡ Response within 24–48 hours\n"
        "🔒 Secure & private\n"
        "📋 Takes under 2 minutes\n\n"
        "Ready to see if you qualify?",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    return STATE_MENU


async def learn_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "ℹ️ *About Cairn Credit*\n\n"
        "Cairn Credit is a US micro-finance lender specialising in personal loans "
        "for people the banking system has overlooked.\n\n"
        "🔍 *How it works:*\n"
        "1. Answer 5 quick questions\n"
        "2. A real team member reviews your application\n"
        "3. We contact you within 24–48 hours\n\n"
        "💬 We look at your *full situation*, not just a credit score number.\n\n"
        "Ready to check if you qualify?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Start Eligibility Check", callback_data="start_quiz")],
        ]),
    )
    return STATE_MENU


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Great! Let's get started. This takes about 2 minutes. 🚀\n\n"
        "*Question 1 of 5*\n"
        "📍 Which US state are you in?",
        parse_mode="Markdown",
        reply_markup=us_states(),
    )
    return STATE_STATE


async def got_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    state_name = query.data.replace("state_", "")
    context.user_data["state"] = state_name

    await query.edit_message_text(
        f"📍 State: *{state_name}* ✅\n\n"
        "*Question 2 of 5*\n"
        "💰 How much are you looking to borrow?",
        parse_mode="Markdown",
        reply_markup=amount_keyboard(),
    )
    return STATE_AMOUNT


async def got_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    amount = query.data.replace("amount_", "")
    context.user_data["amount"] = amount

    await query.edit_message_text(
        f"💰 Amount: *${amount}* ✅\n\n"
        "*Question 3 of 5*\n"
        "📊 How would you describe your credit score?",
        parse_mode="Markdown",
        reply_markup=credit_keyboard(),
    )
    return STATE_CREDIT


async def got_credit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    credit = query.data.replace("credit_", "")
    context.user_data["credit"] = credit

    await query.edit_message_text(
        f"📊 Credit: *{credit.title()}* ✅\n\n"
        "*Question 4 of 5*\n"
        "💼 Do you have employment or regular income?",
        parse_mode="Markdown",
        reply_markup=income_keyboard(),
    )
    return STATE_INCOME


async def got_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data.replace("income_", "")
    context.user_data["income"] = income

    await query.edit_message_text(
        f"💼 Income: *{income.title()}* ✅\n\n"
        "*Question 5 of 5*\n"
        "🏦 Have you been declined for a loan before?",
        parse_mode="Markdown",
        reply_markup=declined_keyboard(),
    )
    return STATE_DECLINED


async def got_declined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    declined = query.data.replace("declined_", "")
    context.user_data["declined"] = declined

    await query.edit_message_text(
        "✅ *Quiz complete!*\n\n"
        "Based on your answers, you may qualify for a Cairn Credit review. "
        "A real person will look at your full situation — not just a number.\n\n"
        "To get started, I just need a few contact details.\n\n"
        "👤 *What's your full name?*",
        parse_mode="Markdown",
    )
    return STATE_NAME


async def got_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("Please enter your full name.")
        return STATE_NAME
    context.user_data["name"] = name
    await update.message.reply_text(
        f"Nice to meet you, *{name}*! 👋\n\n"
        "📧 *What's your email address?*\n"
        "_We'll send your application confirmation here._",
        parse_mode="Markdown",
    )
    return STATE_EMAIL


async def got_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if "@" not in email or "." not in email:
        await update.message.reply_text("That doesn't look like a valid email. Please try again.")
        return STATE_EMAIL
    context.user_data["email"] = email
    await update.message.reply_text(
        "📧 Email saved ✅\n\n"
        "📞 *What's your phone number?*\n"
        "_Our team will call you within 24–48 hours._",
        parse_mode="Markdown",
    )
    return STATE_PHONE


async def got_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if len(phone) < 7:
        await update.message.reply_text("Please enter a valid phone number.")
        return STATE_PHONE
    context.user_data["phone"] = phone
    lead = context.user_data

    # Send confirmation to user FIRST — never let email block this
    await update.message.reply_text(
        "🎉 *Application Received — Thank You!*\n\n"
        f"Hi *{lead.get('name')}*, your application has been submitted successfully.\n\n"
        "📋 *Your summary:*\n"
        f"📍 State: {lead.get('state')}\n"
        f"💰 Loan Amount: ${lead.get('amount')}\n"
        f"📊 Credit: {lead.get('credit', '').title()}\n"
        f"💼 Income: {lead.get('income', '').title()}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📞 *What happens next?*\n\n"
        "A real Cairn Credit team member will personally review your application "
        "and reach out to you by *phone or email within 24 hours* — often sooner.\n\n"
        "You don't need to do anything else. Sit tight and we'll be in touch! 💪\n\n"
        "🌐 _Learn more at cairn-credit.vercel.app_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Visit Cairn Credit", url="https://cairn-credit.vercel.app")],
            [InlineKeyboardButton("🔄 Start New Application", callback_data="restart")],
        ]),
    )

    # Send email in background — won't block or freeze the bot
    try:
        send_lead_email(lead)
        logger.info(f"Lead email sent for {lead.get('name')}")
    except Exception as e:
        logger.error(f"Email failed for {lead.get('name')}: {e}")

    return STATE_DONE


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text(
        "👋 *Welcome back to Cairn Credit!*\n\n"
        "Ready to check eligibility for a new application?",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    return STATE_MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "No problem! Type /start whenever you're ready to apply. 👋"
    )
    return ConversationHandler.END


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I didn't quite get that. Type /start to begin your loan eligibility check."
    )


# ── Wire everything together ─────────────────────────────────────────────────

def setup_handlers(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STATE_MENU: [
                CallbackQueryHandler(start_quiz, pattern="^start_quiz$"),
                CallbackQueryHandler(learn_more, pattern="^learn_more$"),
            ],
            STATE_STATE: [
                CallbackQueryHandler(got_state, pattern="^state_"),
            ],
            STATE_AMOUNT: [
                CallbackQueryHandler(got_amount, pattern="^amount_"),
            ],
            STATE_CREDIT: [
                CallbackQueryHandler(got_credit, pattern="^credit_"),
            ],
            STATE_INCOME: [
                CallbackQueryHandler(got_income, pattern="^income_"),
            ],
            STATE_DECLINED: [
                CallbackQueryHandler(got_declined, pattern="^declined_"),
            ],
            STATE_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, got_name),
            ],
            STATE_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, got_email),
            ],
            STATE_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, got_phone),
            ],
            STATE_DONE: [
                CallbackQueryHandler(restart, pattern="^restart$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
