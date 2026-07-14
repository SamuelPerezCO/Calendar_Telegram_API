"""
t.me/Calendar_Telegram12_Bot.
"""
from telegram.ext import ApplicationBuilder , CommandHandler
from telegram import Update
from dotenv import load_dotenv
import os

from Controllers.calendarController import calendarController

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler( CommandHandler("start" , calendarController.show_menu))


application.run_polling(allowed_updates=Update.ALL_TYPES)