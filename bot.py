import os
import time
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

START_TIME = time.time()
last_events = []


def log_event(text):
    last_events.append(f"{datetime.now().strftime('%H:%M:%S')} - {text}")
    if len(last_events) > 10:
        last_events.pop(0)


# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot online!")


# --- ECHO ---
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        log_event(update.message.text)
        await update.message.reply_text(update.message.text)


# --- PING ---
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!")


# --- STATO ---
async def stato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = round(time.time() - START_TIME, 2)

    try:
        api_start = time.time()
        requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe")
        api_latency = round((time.time() - api_start) * 1000, 2)
    except:
        api_latency = -1

    await update.message.reply_text(
        f"📊 STATO BOT\n\n"
        f"⏱ Uptime: {uptime}s\n"
        f"🌐 Telegram API: {api_latency} ms"
    )


# --- ULTIMI ---
async def ultimi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not last_events:
        await update.message.reply_text("Nessun evento ancora.")
        return

    await update.message.reply_text("🧾 ULTIMI EVENTI:\n\n" + "\n".join(last_events))


# --- APP ---
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("stato", stato))
app.add_handler(CommandHandler("ultimi", ultimi))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()
