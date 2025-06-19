# Amul Product Notifier Bot - Architecture & Logic

## Overview
This project automates the process of fetching Amul product API cookies and headers for a large list of Indian city pincodes, updates a GitHub Gist with the results, and provides a Telegram bot for users to subscribe to product notifications by pincode.

---

## High-Level Architecture Diagram

```
+-------------------+         +-------------------+         +-------------------+
|                   |         |                   |         |                   |
|  Selenium Script  +-------->+   GitHub Gist     +<--------+  GitHub Actions   |
| (fetch_cookie_... |         | (API URL &        |         | (Scheduler: runs  |
|  _and_update.py)  |         |  cookies/headers) |         |  script every 2h) |
+-------------------+         +-------------------+         +-------------------+
        |                                                         ^
        |                                                         |
        v                                                         |
+-------------------+         +-------------------+         +-------------------+
|                   |         |                   |         |                   |
|  pincodes.txt     |         |  products.json    |         |  subscriptions... |
| (all supported    |         | (product info)    |         | (user subs)       |
|  pincodes)        |         |                   |         |                   |
+-------------------+         +-------------------+         +-------------------+
        |
        v
+-------------------+
|                   |
|  Telegram Bot     |
|  (bot_main.py)    |
|                   |
+-------------------+
```

---

## Main Components & Logic

### 1. Selenium Script (`fetch_cookie_and_update.py`)
- Reads all pincodes from `pincodes.txt`.
- For each pincode:
    - Launches a headless browser using Selenium.
    - Navigates to the Amul shop site for that pincode.
    - Extracts the actual Amul API URL and cookies from browser network logs.
    - Updates a GitHub Gist with a mapping: `{pincode: {API_URL, COOKIE}}`.
- Can be run locally or via GitHub Actions (scheduled every 2 hours).

### 2. GitHub Actions Workflow
- Runs the Selenium script every 2 hours (or manually).
- Ensures the Gist is always up-to-date with fresh cookies and API URLs for all supported pincodes.

### 3. Telegram Bot (`bot_main.py`)
- Users interact with the bot to subscribe to product notifications.
- Flow:
    1. User starts the bot or uses `/products`.
    2. Bot asks for the user's pincode and validates it against `pincodes.txt`.
    3. If valid, bot shows available products for subscription.
    4. User selects a product and confirms subscription for their pincode.
    5. Bot stores the subscription in `subscriptions.json`.
    6. (Optional) Notifier logic can alert users when product status changes.

### 4. Data Files
- `pincodes.txt`: List of all supported pincodes (major Indian cities).
- `products.json`: Product catalog (used by the bot).
- `subscriptions.json`: User subscriptions (used by the bot).

---

## Key Logic Points
- **Deduplication & Validation:** Pincodes are deduplicated and validated before processing.
- **Incremental Gist Update:** Gist is updated after each pincode is processed, so partial results are always saved.
- **Error Handling:** If a pincode is not supported, the bot informs the user.
- **Separation of Concerns:** Browser automation, data storage, and user interaction are cleanly separated.

---

## How It All Fits Together
- The Selenium script keeps the API access info fresh for all pincodes.
- The Telegram bot uses this info to provide accurate, up-to-date product tracking and notifications for users.
- All data is versioned and managed via GitHub and Gist for transparency and automation.

---

## (Optional) Sequence Diagram

```
User -> Telegram Bot: /products
Telegram Bot -> User: Please enter your 6-digit delivery pincode:
User -> Telegram Bot: 110001
Telegram Bot -> User: [Shows product list]
User -> Telegram Bot: [Selects product]
Telegram Bot -> User: Subscribed to [product] for pincode 110001!
```

---

For more details, see the code and README.
