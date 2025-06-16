# 🚀 Telegram Group Pastebin

## ✨ Overview

**Telegram Group Pastebin** is a simple, self-hosted solution that transforms any Telegram group chat into a public read/write web interface.

Imagine a shared whiteboard or a basic pastebin — but directly synced with your Telegram group. Anyone with access to the web interface can:

- 📝 View the conversation history
- 📤 Post new messages that appear instantly in the Telegram group

## 🔧 How It Works

- 🌐 A **Flask web server** powers the frontend interface.
- 🤖 A **Python Telegram bot** handles communication with your Telegram group.
- 💾 All messages are stored in a simple `messages.json` file, ensuring persistent message history.
- 📦 Entire setup is **containerized using Docker Compose** for easy deployment.

## 📂 Features

- Public and writeable web interface
- Real-time message sync between web and Telegram
- Lightweight and easy to host
- Persistent message storage via `messages.json`

## 🐳 Deployment

The entire project runs inside Docker containers using `docker-compose`.

```bash
git clone https://github.com/ayyya6969/TelegramGroupPastebin.git
cd telegram-group-pastebin
cp .env.example .env  # Fill in your Telegram bot token and group chat ID
docker-compose up -d
```

## 📄 Requirements

- Docker & Docker Compose
- Telegram bot token (via [@BotFather](https://t.me/BotFather))
- Telegram group chat ID

## 📬 Getting Started

1. Create a new bot with [@BotFather](https://t.me/BotFather).
2. Add the bot to your group and promote it as an admin.
3. Update the `.env` file with your bot token and chat ID.
4. Deploy with Docker Compose.

## 🛡️ Security Note

This pastebin is publicly writable. Consider adding authentication if exposing it to the internet.
