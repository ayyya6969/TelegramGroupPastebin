import json
import os
import time
import requests
import threading
from datetime import datetime
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Now pulling directly from loaded environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_GROUP_CHAT_ID:
    print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_GROUP_CHAT_ID not found in environment variables (check .env file or system settings).")
    print("Please ensure these are set up correctly for the bot to function.")
    exit(1) # Exit if critical variables are missing

TELEGRAM_API_BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"
MESSAGES_FILE = 'messages.json'
LAST_UPDATE_ID = 0

# --- JSON Database Functions (no change) ---
def load_messages():
    """Loads messages from the JSON file."""
    if not os.path.exists(MESSAGES_FILE) or os.stat(MESSAGES_FILE).st_size == 0:
        return []
    try:
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: {MESSAGES_FILE} is empty or malformed. Starting with empty list.")
        return []

def save_message(message):
    """Appends a new message to the JSON file."""
    messages = load_messages()
    messages.append(message)
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)

def send_telegram_message(chat_id, text):
    """Sends a message to a specific chat in Telegram."""
    url = TELEGRAM_API_BASE_URL + "sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"Sent message to Telegram: {text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")
        return None

def process_telegram_updates():
    """Polls Telegram for new messages and processes them."""
    global LAST_UPDATE_ID
    offset = LAST_UPDATE_ID + 1 if LAST_UPDATE_ID else 0
    url = TELEGRAM_API_BASE_URL + f"getUpdates?offset={offset}&timeout=30"

    try:
        response = requests.get(url)
        response.raise_for_status()
        updates = response.json().get('result', [])

        for update in updates:
            LAST_UPDATE_ID = max(LAST_UPDATE_ID, update['update_id'])
            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                text = message.get('text')
                sender_name = message['from'].get('first_name', 'Unknown')
                message_timestamp = datetime.fromtimestamp(message['date']).isoformat()

                # Ensure we only process messages from our target group chat
                if text and str(chat_id) == TELEGRAM_GROUP_CHAT_ID:
                    print(f"Received from Telegram ({sender_name} in chat {chat_id}): {text}")
                    new_message = {
                        "source": "telegram",
                        "from": sender_name,
                        "text": text,
                        "timestamp": message_timestamp
                    }
                    save_message(new_message)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching updates from Telegram: {e}")
    except json.JSONDecodeError:
        print("Error decoding JSON from Telegram API response.")

def bot_polling_loop():
    """Continuously polls Telegram for updates."""
    print("Telegram bot polling started...")
    while True:
        process_telegram_updates()
        time.sleep(1)

if __name__ == '__main__':
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

    bot_thread = threading.Thread(target=bot_polling_loop)
    bot_thread.daemon = True
    bot_thread.start()

    print("Telegram bot is running in the background.")
    print("You can now run 'app.py' in a separate terminal to start the web server.")
    print("Press Ctrl+C to exit this bot script.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nBot script terminated.")