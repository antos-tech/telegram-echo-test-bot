import os
import time
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# --- uptime tracking ---
START_TIME = time.time()

# --- simple event memory ---
last_events = []


def log_event(text: str):
    global last_events
    last_events.append(f"{datetime.now().strftime('%H:%M:%S')} - {text}")
    if len(last_events) > 10:
        last_events.pop(0)


# --- echo ---
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        log_event(f"MSG: {update.message.text}")
        await update.message.reply_text(update.message.text)


# --- ping ---
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    await update.message.reply_text(f"Pong {round((time.time()-start)*1000, 2)} ms")


# --- stato ---
async def stato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()

    # Telegram API latency
    api_start = time.time()
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe")
        api_latency = round((time.time() - api_start) * 1000, 2)
    except:
        api_latency = -1

    bot_latency = round((time.time() - start) * 1000, 2)
    uptime = round(time.time() - START_TIME, 2)

    msg = (
        "📊 BOT STATUS\n\n"
        f"⚡ Bot latency: {bot_latency} ms\n"
        f"🌐 Telegram API: {api_latency} ms\n"
        f"⏱ Uptime: {uptime} sec\n"
    )

    await update.message.reply_text(msg)


# --- info ---
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = round(time.time() - START_TIME, 2)

    await update.message.reply_text(
        "ℹ️ BOT INFO\n\n"
        f"⏱ Uptime: {uptime} sec\n"
        "🤖 Type: Echo + Monitor Bot\n"
        "⚙️ Runtime: Railway"
    )


# --- last events ---
async def ultimi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not last_events:
        await update.message.reply_text("Nessun evento registrato ancora.")
        return

    text = "🧾 ULTIMI EVENTI:\n\n" + "\n".join(last_events)
    await update.message.reply_text(text)


# --- app setup ---
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("stato", stato))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("ultimi", ultimi))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()
