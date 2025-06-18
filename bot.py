import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

waiting_users = []
active_chats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_chats:
        await update.message.reply_text("You're already chatting! Send /stop to end it.")
        return

    if user_id in waiting_users:
        await update.message.reply_text("You're already in the waiting queue...")
        return

    if waiting_users:
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        await context.bot.send_message(partner_id, "🎉 Connected to a stranger! Say hi!")
        await update.message.reply_text("🎉 Connected to a stranger! Say hi!")
    else:
        waiting_users.append(user_id)
        await update.message.reply_text("⏳ Waiting for a stranger to connect...")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = active_chats.pop(user_id, None)
    if partner_id:
        active_chats.pop(partner_id, None)
        await context.bot.send_message(partner_id, "❌ Stranger has left the chat.")
        await update.message.reply_text("❌ You left the chat.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        await update.message.reply_text("❌ You left the queue.")
    else:
        await update.message.reply_text("⚠️ You're not in a chat.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = active_chats.get(user_id)
    if partner_id:
        try:
            if update.message.text:
                await context.bot.send_message(partner_id, update.message.text)
            elif update.message.sticker:
                await context.bot.send_sticker(partner_id, update.message.sticker.file_id)
            elif update.message.photo:
                await context.bot.send_photo(partner_id, update.message.photo[-1].file_id)
            elif update.message.video:
                await context.bot.send_video(partner_id, update.message.video.file_id)
            elif update.message.voice:
                await context.bot.send_voice(partner_id, update.message.voice.file_id)
        except Exception:
            await update.message.reply_text("❌ Error delivering message.")
    else:
        await update.message.reply_text("⚠️ You're not in a chat. Use /start to find someone.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(MessageHandler(filters.ALL, message_handler))

keep_alive()
print("Bot is running...")
app.run_polling()
