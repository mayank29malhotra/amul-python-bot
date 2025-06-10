
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store user preferences
user_preferences = {}
bot_instance = None  # Will be set after bot is initialized

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /setproduct <product name> to track a product.")

# Set product command
async def setproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    product_name = ' '.join(context.args)
    if not product_name:
        await update.message.reply_text("Please provide a product name.")
        return
    user_preferences[user_id] = product_name
    await update.message.reply_text(f"Tracking product: {product_name}")

# Check product availability
def check_availability():
    url = "https://shop.amul.com/en/browse/protein"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()

        for user_id, product in user_preferences.items():
            if product.lower() in page_text:
                bot_instance.send_message(chat_id=user_id, text=f"✅ '{product}' is back in stock!")
    except Exception as e:
        logger.error(f"Error checking availability: {e}")

# Main function
async def main():
    global bot_instance
    application = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN").build()
    bot_instance = application.bot

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setproduct", setproduct))

    # Scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_availability, 'interval', minutes=10)
    scheduler.start()

    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
