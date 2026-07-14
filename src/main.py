"""
t.me/Calendar_Telegram12_Bot.
"""
from telegram.ext import ApplicationBuilder
from telegram import Update
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

application = ApplicationBuilder().token(BOT_TOKEN).build()

application.run_polling(allowed_updates=Update.ALL_TYPES)