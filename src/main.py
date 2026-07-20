"""
t.me/Calendar_Telegram12_Bot.
"""
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters

from telegram import Update
from dotenv import load_dotenv
import os

# TITLE, DATE, TIME are the conversation states defined in the controller —
# main.py needs them to tell the ConversationHandler which handler runs in which state
from Controllers.calendarController import calendarController, TITLE, DATE, TIME

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler( CommandHandler("start" , calendarController.show_menu))

application.add_handler(MessageHandler(filters.Regex("^Create Task or Event$"), calendarController.create_task_or_event))

# The create-event flow is a ConversationHandler: a small state machine that
# asks one question at a time and remembers where each user is in the flow.
create_event_conversation = ConversationHandler(
    # entry_points: what STARTS the conversation — tapping "Create a Event"
    entry_points=[MessageHandler(filters.Regex("^Create a Event$"), calendarController.create_event_start)],
    # states: for each state, which handler processes the user's next message.
    # filters.TEXT & ~filters.COMMAND = "any text that is not a /command",
    # so /cancel is not swallowed as if it were a title or a date.
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calendarController.create_event_title)],
        DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calendarController.create_event_date)],
        TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, calendarController.create_event_time)],
    },
    # fallbacks: handlers that work in ANY state — /cancel aborts the flow
    fallbacks=[CommandHandler("cancel", calendarController.cancel)],
)
application.add_handler(create_event_conversation)

application.run_polling(allowed_updates=Update.ALL_TYPES)