import os
import time
import requests
import threading
from datetime import datetime
from dotenv import load_dotenv
import db_manager

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_GROUP_CHAT_ID:
    print("FATAL ERROR: Telegram bot token or group chat ID missing from .env. Bot will not run.")
    exit(1)

TELEGRAM_API_BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"
LAST_UPDATE_ID = 0
# COMMAND_PREFIX = "/post" # Removed as any message will be posted

def process_telegram_updates():
    """Poll Telegram for new messages and process them."""
    global LAST_UPDATE_ID
    offset = LAST_UPDATE_ID + 1 if LAST_UPDATE_ID else 0
    url = TELEGRAM_API_BASE_URL + f"getUpdates?offset={offset}&timeout=30"

    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        updates = response.json().get('result', [])

        if updates:
            print(f"[DEBUG] Received {len(updates)} update(s).")

        for update in updates:
            LAST_UPDATE_ID = max(LAST_UPDATE_ID, update['update_id'])

            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                text = message.get('text') # Safely get text, might be None for non-text messages
                sender_name = message['from'].get('first_name', 'Unknown')
                msg_timestamp = datetime.fromtimestamp(message['date']).isoformat()
                telegram_message_id = message['message_id']

                print(f"[DEBUG] Processing message: Chat ID: {chat_id}, Expected Group ID: {TELEGRAM_GROUP_CHAT_ID}, Text: '{text}', From: {sender_name}")

                # 1. Filter by correct group chat ID
                if str(chat_id) == TELEGRAM_GROUP_CHAT_ID:
                    print(f"[DEBUG] Message is from the configured group: {TELEGRAM_GROUP_CHAT_ID}")

                    # Only process text messages (ignore photos, stickers, etc.)
                    if text:
                        print(f"[INFO] Saving message from Telegram (from {sender_name}): '{text}'")
                        db_manager.add_message( # <--- This line saves to DB
                            source="telegram",
                            sender=sender_name,
                            message_text=text, # Save the entire text
                            timestamp=msg_timestamp,
                            telegram_message_id=telegram_message_id
                        )
                    else:
                        print(f"[INFO] Skipping non-text message from {sender_name} in configured group.")
                else:
                    print(f"[INFO] Skipping message from {sender_name}: Not from the configured group chat ({chat_id}).")

            elif 'edited_message' in update:
                print(f"[DEBUG] Skipping edited message: {update['edited_message'].get('text')}")
            else:
                print(f"[DEBUG] Received non-message update: {update.keys()}")

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error fetching updates from Telegram API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"ERROR: Telegram API Response Status: {e.response.status_code}")
            print(f"ERROR: Telegram API Response Body: {e.response.text}")
        time.sleep(5)
    except Exception as e:
        print(f"CRITICAL ERROR: Uncaught exception in process_telegram_updates: {e}")
        time.sleep(5)

def bot_polling_loop():
    print("Telegram bot polling started...")
    while True:
        process_telegram_updates()
        time.sleep(1)

if __name__ == '__main__':
    db_manager.init_db()

    bot_thread = threading.Thread(target=bot_polling_loop)
    bot_thread.daemon = True
    bot_thread.start()

    print("Bot running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nBot stopped by user (Ctrl+C).")