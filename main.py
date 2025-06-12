import subprocess
import threading
import time
import sys
from flask import Flask
import os

# Use the current Python executable (from venv)
PYTHON_EXEC = sys.executable

# Utility to run a script in a thread
def run_script(script):
    def target():
        subprocess.run([PYTHON_EXEC, script])
    t = threading.Thread(target=target)
    t.daemon = True
    t.start()
    return t

app = Flask(__name__)

@app.route("/")
def home():
    return "Amul bot is running!"

@app.route("/health")
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Start Flask server in a thread
    threading.Thread(target=run_flask, daemon=True).start()
    # Start the Telegram bot (user interaction)
    run_script("bot_main.py")
    # Start the notifier (periodic stock check)
    run_script("notifier.py")
    # Optionally, sync products at startup
    run_script("product_sync.py")
    print("All services started. Running forever...")
    while True:
        time.sleep(60)
