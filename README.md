# Telegram Echo Bot 🤖

A simple Telegram bot that repeats back any message it receives (echo bot).
It is mainly used to test message delivery between Telegram and a backend service.

---

## 🚀 Features

- Echoes back any text message sent to the bot
- Ignores commands like "/start"
- Easy to deploy on Railway or similar platforms

---

## 📦 Requirements

- Python 3.10 or higher
- A Telegram bot token from BotFather

---

## ⚙️ Installation

1. Clone the repository:

git clone https://github.com/your-username/telegram-echo-bot.git
cd telegram-echo-bot

2. Install dependencies:

pip install -r requirements.txt

---

## 🔑 Configuration

Set the environment variable:

BOT_TOKEN=your_telegram_bot_token

On Railway:

- Go to Variables
- Add "BOT_TOKEN"

---

## ▶️ Run locally

python bot.py

---

## ☁️ Deploy on Railway

1. Connect your GitHub repository to Railway
2. Add the environment variable "BOT_TOKEN"
3. Deploy the project
4. The bot will start automatically

---

## 📁 If you want to download (Windows)

Download the source code on the "Releases" section.

---

## 🧠 How it works

The bot uses "python-telegram-bot" in polling mode.
When a message is received, it sends the exact same text back to the user.

---

## 📜 License

This project is open-source and released under the MIT License.

You are free to use, modify, and distribute this project with attribution.

See the LICENSE file for more details.
