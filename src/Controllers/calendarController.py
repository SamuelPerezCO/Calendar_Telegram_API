import asyncio
from datetime import datetime, timedelta

from telegram import Update , ReplyKeyboardMarkup , KeyboardButton , ReplyKeyboardRemove
from telegram.ext import ContextTypes , ConversationHandler

from Services import calendarService

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

    @staticmethod
    async def create_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("What is the title of the event?" , reply_markup=ReplyKeyboardRemove())
        return TITLE 

    @staticmethod
    async def create_event_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["title"] = update.message.text
        await update.message.reply_text("What date? (DD/MM/YYYY, for example 25/07/2026)")
        return DATE  

    @staticmethod
    async def create_event_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            date = datetime.strptime(update.message.text, "%d/%m/%Y").date()
        except ValueError:
            await update.message.reply_text("I couldn't understand that date. Please use DD/MM/YYYY, for example 25/07/2026")
            return DATE
        context.user_data["date"] = date
        await update.message.reply_text("What time does it start? (HH:MM in 24h format, for example 14:30)")
        return TIME  

    @staticmethod
    async def create_event_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            time = datetime.strptime(update.message.text, "%H:%M").time()
        except ValueError:
            await update.message.reply_text("I couldn't understand that time. Please use HH:MM, for example 14:30")
            return TIME

        start = datetime.combine(context.user_data["date"], time).astimezone()
        end = start + timedelta(hours=1)  

        if start < datetime.now().astimezone():
            await update.message.reply_text("That moment is in the past. Please send a future time (HH:MM), or /cancel")
            return TIME

        event = await asyncio.to_thread(
            calendarService.create_event, context.user_data["title"], start, end
        )

        await update.message.reply_text(f"Event created!\n{event.get('htmlLink')}")
        return ConversationHandler.END  

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Okay, cancelled. Send /start to see the menu again.")
        return ConversationHandler.END
