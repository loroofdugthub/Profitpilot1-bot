import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import openai
import requests

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to ProfitPilot! Use /price <symbol> for stock price or /crypto <symbol> for crypto price.")

def get_stock_price(symbol: str):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url).json()
    try:
        price = response['Global Quote']['05. price']
        return price
    except KeyError:
        return None

def price(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_text("Please provide a stock symbol, e.g. /price TSLA")
        return
    symbol = context.args[0].upper()
    price = get_stock_price(symbol)
    if price:
        update.message.reply_text(f"The current price of {symbol} is ${price}")
    else:
        update.message.reply_text(f"Could not fetch price for {symbol}. Try again later.")

def crypto(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_text("Please provide a crypto symbol, e.g. /crypto BTC")
        return
    symbol = context.args[0].upper()
    prompt = f"Give a quick trading tip for crypto symbol {symbol}"
    try:
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=50,
            temperature=0.7,
        )
        tip = response.choices[0].text.strip()
        update.message.reply_text(f"Trading tip for {symbol}:\n{tip}")
    except Exception as e:
        update.message.reply_text("Sorry, couldn't fetch tip now.")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("crypto", crypto))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
