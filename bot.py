import os
import time
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")


# --- ECHO ---
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)


# --- STATO COMMAND ---
async def stato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()

    # misura latenza verso Telegram API
    api_start = time.time()
    requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe")
    api_latency = round((time.time() - api_start) * 1000, 2)

    bot_latency = round((time.time() - start) * 1000, 2)

    region = os.getenv("RAILWAY_REGION", "unknown (check Railway dashboard)")

    msg = (
        "📊 Bot Status\n\n"
        f"⚡ Bot latency: {bot_latency} ms\n"
        f"🌐 Telegram API latency: {api_latency} ms\n"
        f"📍 Region: {region}"
    )

    await update.message.reply_text(msg)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("stato", stato))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()
