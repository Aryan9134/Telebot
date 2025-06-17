from flask import Flask
import threading
import telebot
from telebot import types
import os

# Flask app for uptime pings
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is Alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# Telegram Bot setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# -------------------------------
# Chat Matching System Placeholder
# -------------------------------

waiting_users = []
active_chats = {}

@bot.message_handler(commands=["start"])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🌐 Change Language", "🔍 Start Chat", "❌ Stop Chat")
    bot.send_message(message.chat.id, "Welcome! Choose an option:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🔍 Start Chat")
def handle_chat_start(message):
    user_id = message.chat.id
    if user_id in active_chats:
        bot.send_message(user_id, "You're already in a chat!")
        return
    if waiting_users:
        partner_id = waiting_users.pop(0)
        if partner_id == user_id:
            waiting_users.append(user_id)
            return
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        bot.send_message(user_id, "🎉 Connected! Say hi.")
        bot.send_message(partner_id, "🎉 Connected! Say hi.")
    else:
        waiting_users.append(user_id)
        bot.send_message(user_id, "⌛ Waiting for someone to join...")

@bot.message_handler(func=lambda message: message.text == "❌ Stop Chat")
def stop_chat(message):
    user_id = message.chat.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        bot.send_message(partner_id, "⚠️ The user left the chat.")
        bot.send_message(user_id, "❌ Chat ended.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        bot.send_message(user_id, "❌ Left the queue.")
    else:
        bot.send_message(user_id, "You're not in a chat.")

@bot.message_handler(func=lambda message: True)
def relay_messages(message):
    user_id = message.chat.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        bot.send_message(partner_id, message.text)

bot.infinity_polling()
                     
