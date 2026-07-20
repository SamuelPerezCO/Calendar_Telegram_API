# asyncio: lets us run the (slow) Google API call without freezing the bot
import asyncio
from datetime import datetime, timedelta

from telegram import Update , ReplyKeyboardMarkup , KeyboardButton , ReplyKeyboardRemove
from telegram.ext import ContextTypes , ConversationHandler

# our own module that talks to Google Calendar (src/Services/calendarService.py)
from Services import calendarService

# The "states" of the create-event conversation. A state = "what answer is the
# bot waiting for right now". The bot moves TITLE -> DATE -> TIME, one question
# at a time. range(3) just gives them values 0, 1, 2 — the numbers don't matter.
TITLE, DATE, TIME = range(3)


class calendarController:

    @staticmethod
    async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("Create Task or Event") , KeyboardButton("Read Task or Event")],
            [KeyboardButton("Update Task or Event") , KeyboardButton("Delete Task or Event")],
            [KeyboardButton("I'm not doing something today")]
        ])
        await update.message.reply_text("Hi! (name of the gmail)\nWhat do you want to do?\nChoose an option " , reply_markup=keyboard)

    @staticmethod
    async def create_task_or_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("Create a Task") , KeyboardButton("Create a Event")]
        ])
        if update.message.text == "Create Task or Event":
            await update.message.reply_text("What do you want to do?" , reply_markup=keyboard)

    # ---------- Create event conversation ----------
    # Each method handles ONE answer from the user and then RETURNS the next
    # state, which tells the ConversationHandler (in main.py) what to wait for.
    # Answers are remembered between steps in context.user_data (a dictionary
    # that Telegram keeps separately for each user).

    @staticmethod
    async def create_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Entry point: runs when the user taps "Create a Event".
        # ReplyKeyboardRemove() hides the menu buttons while we ask questions.
        await update.message.reply_text("What is the title of the event?" , reply_markup=ReplyKeyboardRemove())
        return TITLE  # -> next, wait for the title

    @staticmethod
    async def create_event_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # The user's message here IS the title -> remember it for the final step
        context.user_data["title"] = update.message.text
        await update.message.reply_text("What date? (DD/MM/YYYY, for example 25/07/2026)")
        return DATE  # -> next, wait for the date

    @staticmethod
    async def create_event_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # strptime = "parse this text using this format". If the text doesn't
        # match the format it raises ValueError -> we re-ask and STAY in the
        # DATE state (returning DATE again means "wait for another date").
        try:
            date = datetime.strptime(update.message.text, "%d/%m/%Y").date()
        except ValueError:
            await update.message.reply_text("I couldn't understand that date. Please use DD/MM/YYYY, for example 25/07/2026")
            return DATE
        context.user_data["date"] = date
        await update.message.reply_text("What time does it start? (HH:MM in 24h format, for example 14:30)")
        return TIME  # -> next, wait for the time

    @staticmethod
    async def create_event_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            time = datetime.strptime(update.message.text, "%H:%M").time()
        except ValueError:
            await update.message.reply_text("I couldn't understand that time. Please use HH:MM, for example 14:30")
            return TIME

        # Join the date (asked before) with the time (just received) into one
        # datetime, and .astimezone() attaches your local timezone so Google
        # puts the event at the right hour.
        start = datetime.combine(context.user_data["date"], time).astimezone()
        end = start + timedelta(hours=1)  # default duration: 1 hour

        if start < datetime.now().astimezone():
            await update.message.reply_text("That moment is in the past. Please send a future time (HH:MM), or /cancel")
            return TIME

        # The Google client is synchronous (it blocks while waiting for Google's
        # answer), so we run it in a thread to keep the bot responding to others.
        event = await asyncio.to_thread(
            calendarService.create_event, context.user_data["title"], start, end
        )

        # Google returns the created event; "htmlLink" is a URL to open it in Calendar
        await update.message.reply_text(f"Event created!\n{event.get('htmlLink')}")
        return ConversationHandler.END  # conversation finished

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Runs when the user sends /cancel at any point of the conversation
        await update.message.reply_text("Okay, cancelled. Send /start to see the menu again.")
        return ConversationHandler.END
