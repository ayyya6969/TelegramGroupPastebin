# Telegram Pastebin with Docker

This project provides a simple web-based pastebin application integrated with Telegram. It allows you to post content from both a web interface and directly from a Telegram group using a specific command. Messages posted are stored in a local SQLite database and displayed on the web interface, with the ability to delete them from the web, which also removes them from Telegram.

---

## ✨ Features

- **Post from Web to Telegram**  
  Easily send messages from the web interface to your designated Telegram group.

- **Post from Telegram to Web**  
  Use the `/post` command in your Telegram group to send content directly to your web pastebin.

- **Synchronized Deletion**  
  Delete messages from the web interface, and they will also be removed from the Telegram group.

- **Persistent Storage**  
  Messages are saved using a SQLite database (`messages.db`) for persistence across restarts.

- **Containerized Deployment**  
  Simple setup and deployment using Docker and Docker Compose.

---

## 🔧 Technologies Used

- **Python 3**: The core programming language.
- **Flask**: A lightweight web framework for the web interface.
- **SQLite**: A file-based database for storing messages.
- **Telegram Bot API**: For interaction with Telegram.
- **Docker**: For containerization of the application services.
- **Docker Compose**: For defining and running the multi-container Docker application.

---

## ✅ Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Docker**  
  This includes Docker Engine and Docker Compose.
