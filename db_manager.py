import sqlite3
import os

DB_NAME = 'messages.db'

def init_db():
    """Initializes the SQLite database, creating the messages table if it doesn't exist.
    Adds telegram_message_id column for linking to Telegram messages.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,      -- 'web' or 'telegram'
            sender TEXT NOT NULL,      -- e.g., 'Web User', Telegram username/first_name
            message_text TEXT NOT NULL,
            timestamp TEXT NOT NULL,   -- ISO 8601 format
            telegram_message_id INTEGER -- Telegram's message ID, NULL if not applicable or not yet sent
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized successfully.")

def add_message(source, sender, message_text, timestamp, telegram_message_id=None):
    """Adds a new message to the database, including Telegram's message ID if provided."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO messages (source, sender, message_text, timestamp, telegram_message_id) VALUES (?, ?, ?, ?, ?)",
                       (source, sender, message_text, timestamp, telegram_message_id))
        conn.commit()
        # Return the last inserted row ID (our internal DB ID)
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error adding message to DB: {e}")
        return None
    finally:
        conn.close()

def get_messages(limit=100):
    """Retrieves the latest messages from the database, including their internal DB ID and Telegram ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, source, sender, message_text, timestamp, telegram_message_id FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    messages_raw = cursor.fetchall()
    conn.close()

    formatted_messages = []
    for msg in reversed(messages_raw):
        formatted_messages.append({
            "id": msg[0], # Our internal DB ID
            "source": msg[1],
            "from": msg[2],
            "text": msg[3],
            "timestamp": msg[4],
            "telegram_message_id": msg[5] # Telegram's message ID
        })
    return formatted_messages

def get_message_by_id(db_id):
    """Retrieves a single message by its internal database ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, source, sender, message_text, timestamp, telegram_message_id FROM messages WHERE id = ?", (db_id,))
    msg = cursor.fetchone()
    conn.close()
    if msg:
        return {
            "id": msg[0],
            "source": msg[1],
            "from": msg[2],
            "text": msg[3],
            "timestamp": msg[4],
            "telegram_message_id": msg[5]
        }
    return None

def update_telegram_message_id(db_id, telegram_message_id):
    """Updates the telegram_message_id for a given internal DB ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE messages SET telegram_message_id = ? WHERE id = ?", (telegram_message_id, db_id))
        conn.commit()
        print(f"Updated DB message ID {db_id} with Telegram message ID {telegram_message_id}")
        return True
    except sqlite3.Error as e:
        print(f"Error updating Telegram message ID in DB: {e}")
        return False
    finally:
        conn.close()

def delete_message_by_id(db_id):
    """Deletes a message from the database by its internal ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM messages WHERE id = ?", (db_id,))
        conn.commit()
        print(f"Deleted message with DB ID: {db_id} from database.")
        return True
    except sqlite3.Error as e:
        print(f"Error deleting message from DB: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    # This block runs if db_manager.py is executed directly
    init_db()
    # Example usage:
    # from datetime import datetime
    # new_db_id = add_message("test_source", "TestUser", "Hello from test!", datetime.now().isoformat(), 12345)
    # print(f"New message added with DB ID: {new_db_id}")
    # msgs = get_messages()
    # print(msgs)
    # msg_to_del = get_message_by_id(new_db_id)
    # if msg_to_del:
    #     print(f"Fetched message for deletion: {msg_to_del}")
    #     delete_message_by_id(new_db_id)
    #     print("Messages after deletion:", get_messages())