import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import db_manager # Import our new db_manager

load_dotenv() # Load environment variables from .env

app = Flask(__name__)

# --- Telegram API Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")
TELEGRAM_API_BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/" if TELEGRAM_BOT_TOKEN else None

# --- Telegram Sending/Deleting Function ---
def send_to_telegram(chat_id, text):
    """Send message to Telegram."""
    if not TELEGRAM_API_BASE_URL: return None # Return None on config error
    try:
        response = requests.post(TELEGRAM_API_BASE_URL + "sendMessage", data={'chat_id': chat_id, 'text': text})
        response.raise_for_status()
        result = response.json()
        print(f"Sent to Telegram: '{text}', Telegram msg ID: {result['result']['message_id']}")
        return result['result']['message_id'] # Return Telegram's message_id
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Telegram: {e}")
        return None

def delete_from_telegram(chat_id, telegram_message_id):
    """Delete message from Telegram."""
    if not TELEGRAM_API_BASE_URL: return False
    try:
        response = requests.post(TELEGRAM_API_BASE_URL + "deleteMessage", data={'chat_id': chat_id, 'message_id': telegram_message_id})
        response.raise_for_status()
        print(f"Deleted Telegram message ID: {telegram_message_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting from Telegram: {e}")
        # Telegram API returns 400 if message is already deleted or too old to delete
        if response.status_code == 400 and "message can't be deleted" in str(e):
            print("Message might already be deleted or too old to delete on Telegram.")
        return False

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_messages', methods=['GET'])
def get_messages():
    messages = db_manager.get_messages(limit=100)
    return jsonify(messages)

@app.route('/send_message_from_web', methods=['POST'])
def send_message_from_web():
    user_message = request.form.get('message')
    if not user_message:
        return jsonify({"status": "error", "message": "Message cannot be empty"}), 400

    timestamp = request.form.get('timestamp')
    
    # Store initial message with no Telegram ID yet
    db_id = db_manager.add_message(source="web", sender="Web User", message_text=user_message, timestamp=timestamp, telegram_message_id=None)

    telegram_msg_id = None
    if TELEGRAM_GROUP_CHAT_ID and db_id is not None:
        telegram_msg_id = send_to_telegram(TELEGRAM_GROUP_CHAT_ID, user_message)
        if telegram_msg_id:
            # Update the message in DB with its Telegram message ID
            db_manager.update_telegram_message_id(db_id, telegram_msg_id)
        else:
            print("Warning: Message sent from web but failed to send to Telegram API.")
    
    if telegram_msg_id is None and TELEGRAM_GROUP_CHAT_ID:
        # If Telegram config is present but sending failed
        return jsonify({"status": "warning", "message": "Message saved to DB, but failed to send to Telegram."}), 200
    elif not TELEGRAM_GROUP_CHAT_ID:
        # If Telegram config is missing
        return jsonify({"status": "warning", "message": "Message saved to DB, Telegram integration not configured."}), 200

    return jsonify({"status": "success", "message": "Message sent to Telegram and saved!"})

@app.route('/delete_message', methods=['POST'])
def delete_message():
    db_id = request.json.get('id')
    if not db_id:
        return jsonify({"status": "error", "message": "Missing message ID"}), 400

    message_to_delete = db_manager.get_message_by_id(db_id)

    if not message_to_delete:
        return jsonify({"status": "error", "message": "Message not found in database."}), 404

    # Attempt to delete from Telegram if it has a telegram_message_id and config is present
    telegram_delete_success = True
    if message_to_delete.get('telegram_message_id') and TELEGRAM_GROUP_CHAT_ID:
        telegram_delete_success = delete_from_telegram(TELEGRAM_GROUP_CHAT_ID, message_to_delete['telegram_message_id'])
    elif not TELEGRAM_GROUP_CHAT_ID:
        print("Telegram API not configured, skipping Telegram deletion.")

    # Always attempt to delete from our local database
    db_delete_success = db_manager.delete_message_by_id(db_id)

    if db_delete_success and telegram_delete_success:
        return jsonify({"status": "success", "message": "Message deleted from both."})
    elif db_delete_success and not telegram_delete_success:
        return jsonify({"status": "warning", "message": "Message deleted from DB, but failed to delete from Telegram (may be too old/already deleted)."}), 200
    else: # Only DB deletion failed
        return jsonify({"status": "error", "message": "Failed to delete message from database."}), 500

if __name__ == '__main__':
    db_manager.init_db() # Ensure DB is initialized before app runs
    app.run(debug=True, host='0.0.0.0', port=5000)