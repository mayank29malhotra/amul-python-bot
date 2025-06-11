import subprocess
import threading
import time
import sys

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

if __name__ == "__main__":
    # Start the Telegram bot (user interaction)
    run_script("bot_main.py")
    # Start the notifier (periodic stock check)
    run_script("notifier.py")
    # Optionally, sync products at startup
    run_script("product_sync.py")
    print("All services started. Running forever...")
    while True:
        time.sleep(60)
