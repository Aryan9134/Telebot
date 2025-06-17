from flask import Flask
import threading
import telebot
import os

# Bot setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Flask setup
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is Alive!", 200

# Run Flask in a separate thread
def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# Start bot
bot.infinity_polling()
