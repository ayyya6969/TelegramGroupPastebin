import json
import os
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

MESSAGES_FILE = 'messages.json'
MAX_MESSAGES_TO_LOAD = 100

# --- Telegram API Configuration ---
# Now pulling directly from loaded environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_GROUP_CHAT_ID:
    print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_GROUP_CHAT_ID not found in environment variables (check .env file or system settings).")
    # In a production app, you might want to exit here.
    TELEGRAM_API_BASE_URL = None
else:
    TELEGRAM_API_BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"

# --- JSON Database Functions (no change) ---
def load_messages():
    """Loads messages from the JSON file."""
    if not os.path.exists(MESSAGES_FILE) or os.stat(MESSAGES_FILE).st_size == 0:
        return []
    try:
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_message(message):
    """Appends a new message to the JSON file."""
    messages = load_messages()
    messages.append(message)
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)

# --- Telegram Sending Function (no change) ---
def send_message_to_telegram(chat_id, text):
    """Sends a message to a specific chat in Telegram via the Bot API."""
    if not TELEGRAM_API_BASE_URL:
        print("Telegram API not configured. Cannot send message to Telegram.")
        return False

    url = TELEGRAM_API_BASE_URL + "sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"Sent message to Telegram from web: '{text}'")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram from web: {e}")
        return False

# --- Flask Routes (no change) ---
@app.route('/')
def index():
    """Renders the main web interface."""
    return render_template('index.html')

@app.route('/get_messages', methods=['GET'])
def get_messages():
    """API endpoint to fetch messages for the web interface."""
    messages = load_messages()
    return jsonify(messages[-MAX_MESSAGES_TO_LOAD:])

@app.route('/send_message_from_web', methods=['POST'])
def send_message_from_web():
    """API endpoint to receive messages from the web interface,
    save them, and send them to Telegram."""
    user_message = request.form.get('message')
    if not user_message:
        return jsonify({"status": "error", "message": "Message cannot be empty"}), 400

    new_message = {
        "source": "web",
        "from": "Web User",
        "text": user_message,
        "timestamp": request.form.get('timestamp')
    }
    save_message(new_message)

    if TELEGRAM_GROUP_CHAT_ID:
        send_success = send_message_to_telegram(TELEGRAM_GROUP_CHAT_ID, user_message)
        if not send_success:
            return jsonify({"status": "warning", "message": "Message saved but failed to send to Telegram."}), 200
    else:
        return jsonify({"status": "warning", "message": "Message saved, but Telegram integration is not configured."}), 200

    return jsonify({"status": "success", "message": "Message sent to Telegram and saved!"})

if __name__ == '__main__':
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    app.run(debug=True, host='0.0.0.0', port=5000) # ADD host='0.0.0.0'