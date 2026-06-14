import os
import time
import json
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import JobQueue

TOKEN = os.getenv("BOT_TOKEN")

START_TIME = time.time()

last_events = []

REM_FILE = "reminders.json"
reminders = {}
reminder_id_counter = 0


# -------------------------
# STORAGE FUNCTIONS
# -------------------------
def load_reminders():
    global reminder_id_counter
    try:
        with open(REM_FILE, "r") as f:
            data = json.load(f)

            # ricostruisci id counter
            if data:
                reminder_id_counter = max(map(int, data.keys()))
            return {int(k): v for k, v in data.items()}
    except:
        return {}


def save_reminders():
    with open(REM_FILE, "w") as f:
        json.dump({str(k): v for k, v in reminders.items()}, f)


# carica all'avvio
reminders = load_reminders()


# -------------------------
# LOG EVENTS
# -------------------------
def log_event(text: str):
    last_events.append(f"{datetime.now().strftime('%H:%M:%S')} - {text}")
    if len(last_events) > 10:
        last_events.pop(0)


# -------------------------
# BASIC COMMANDS
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot online!")


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!")


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
        f"🌐 Telegram API: {api_latency} ms\n"
        f"📦 Reminders salvati: {len(reminders)}"
    )


async def ultimi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not last_events:
        await update.message.reply_text("Nessun evento ancora.")
        return

    await update.message.reply_text("🧾 ULTIMI EVENTI:\n\n" + "\n".join(last_events))


# -------------------------
# REMINDER SYSTEM
# -------------------------
def parse_time(time_str: str) -> int:
    if time_str.endswith("s"):
        return int(time_str[:-1])
    if time_str.endswith("m"):
        return int(time_str[:-1]) * 60
    if time_str.endswith("h"):
        return int(time_str[:-1]) * 3600

    formats = [
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S"
    ]

    for fmt in formats:
        try:
            target = datetime.strptime(time_str, fmt)
            return int((target - datetime.now()).total_seconds())
        except:
            pass

    raise ValueError("Formato non valido")


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    rid = job.data["id"]

    if rid in reminders:
        del reminders[rid]
        save_reminders()

    await context.bot.send_message(
        chat_id=job.data["chat_id"],
        text=f"⏰ PROMEMORIA: {job.data['text']}"
    )


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global reminder_id_counter

    try:
        args = context.args

        if len(args) < 2:
            await update.message.reply_text(
                "Uso:\n"
                "/remind 10m testo\n"
                "/remind 20-06-2026 14:30 testo"
            )
            return

        time_str = args[0]
        text = " ".join(args[1:])

        seconds = parse_time(time_str)

        if seconds <= 0:
            await update.message.reply_text("⚠️ Tempo non valido o già passato")
            return

        reminder_id_counter += 1
        rid = reminder_id_counter

        job = context.job_queue.run_once(
            send_reminder,
            when=seconds,
            data={
                "chat_id": update.effective_chat.id,
                "text": text,
                "id": rid
            }
        )

        reminders[rid] = job
        save_reminders()

        await update.message.reply_text(f"⏰ Promemoria creato (ID: {rid})")

    except Exception as e:
        await update.message.reply_text(f"Errore: {e}")


async def remindlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not reminders:
        await update.message.reply_text("Nessun promemoria attivo.")
        return

    msg = "📋 PROMEMORIA ATTIVI:\n\n"
    for rid in reminders:
        msg += f"ID {rid}\n"

    await update.message.reply_text(msg)


async def cancelremind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if not args:
        await update.message.reply_text("Uso: /cancelremind ID")
        return

    try:
        rid = int(args[0])

        job = reminders.get(rid)

        if not job:
            await update.message.reply_text("ID non trovato")
            return

        job.schedule_removal()
        del reminders[rid]
        save_reminders()

        await update.message.reply_text(f"❌ Promemoria {rid} cancellato")

    except:
        await update.message.reply_text("ID non valido")


# -------------------------
# ECHO
# -------------------------
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        log_event(update.message.text)
        await update.message.reply_text(update.message.text)


# -------------------------
# APP SETUP
# -------------------------
app = Application.builder().token(TOKEN).build()

app = (
    Application.builder()
    .token(TOKEN)
    .job_queue(job_queue)
    .build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("stato", stato))
app.add_handler(CommandHandler("ultimi", ultimi))

app.add_handler(CommandHandler("remind", remind))
app.add_handler(CommandHandler("remindlist", remindlist))
app.add_handler(CommandHandler("cancelremind", cancelremind))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()
