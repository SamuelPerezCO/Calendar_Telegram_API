"""
t.me/Calendar_Telegram12_Bot.
"""
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters

from telegram import Update
from dotenv import load_dotenv
import os

from Controllers.calendarController import calendarController, TITLE, DATE, TIME

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler( CommandHandler("start" , calendarController.show_menu))

application.add_handler(MessageHandler(filters.Regex("^Create Task or Event$"), calendarController.create_task_or_event))

create_event_conversation = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^Create a Event$"), calendarController.create_event_start)],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calendarController.create_event_title)],
        DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calendarController.create_event_date)],
        TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, calendarController.create_event_time)],
    },
    fallbacks=[CommandHandler("cancel", calendarController.cancel)],
)
application.add_handler(create_event_conversation)

application.run_polling(allowed_updates=Update.ALL_TYPES)