# Amul Protein Product Tracker Bot

This project is a Python-based Telegram bot system that tracks Amul protein product availability, notifies users, and keeps product/cookie headers up to date. It is deployed as a Web service on Render and Cookie Updation is done by Github Actions and uses file-based JSON storage for persistence.

## Features

- **Product Sync:** Periodically fetches Amul protein product data from the Amul API using up-to-date headers/cookies.
- **User Subscriptions:** Telegram users can subscribe to a product and receive notifications when it comes in or goes out of stock.
- **Notifications:** Sends in-stock/out-of-stock alerts to users via Telegram.
- **Header/Cookie Refresh:** Uses Selenium to fetch fresh API headers/cookies and updates a GitHub Gist for use by the sync script.
- **Cloud Ready:** Can be deployed as a web service (with a minimal Flask server) to stay awake 24/7 on platforms like Render.

## Project Structure

- `main.py` — Launches all services (bot, notifier, product sync, and Flask web server for cloud hosting).
- `bot_main.py` — Telegram bot logic (user subscriptions, product selection, etc.).
- `notifier.py` — Checks product stock and notifies users.
- `product_sync.py` — Fetches product data from Amul API using headers/cookies from a GitHub Gist.
- `fetch_cookie_and_update.py` — Fetches fresh headers/cookies (via Selenium or Browserless) and updates the Gist.
- `db.py` — Thread-safe JSON read/write for products and subscriptions.
- `products.json` — Product data storage.
- `subscriptions.json` — User subscription storage.
- `requirements.txt` — Python dependencies.
- `README.md` — This file.

## Setup & Deployment

### 1. Clone the Repository
```sh
git clone https://github.com/yourusername/amul-python-bot.git
cd amul-python-bot
```

### 2. Install Dependencies
```sh
pip install -r requirements.txt
```

### 3. Set Environment Variables
Set the following environment variables (in your platform's dashboard or `.env` file):
- `TELEGRAM_TOKEN` — Your Telegram bot token
- `GIST_ID` — Your GitHub Gist ID for API headers/cookies
- `GIST_FILENAME` — (Optional) Filename in the Gist (default: `api_url_and_headers.json`)
- `TOKEN_GITHUB` — GitHub token for updating the Gist

### 4. Run the Bot
```sh
python main.py
```

### 5. Deploy to Cloud (Render, Glitch, Fly.io, etc.)
- For always-on operation, deploy as a **web service** (not a background worker) and ensure `main.py` is the entry point.
- The included Flask server keeps the service awake on platforms that require a web endpoint.

## Keeping the Service Awake
- The minimal Flask server in `main.py` responds to `/` requests and is used to keep the service alive on platforms like Render and Glitch.

## Scheduled Header/Cookie Updates
- Use `fetch_cookie_and_update.py` to refresh Amul API headers/cookies and update your Gist.
- Can be scheduled via GitHub Actions or any other scheduler.


---

**Made with ❤️ for Amul fans!**