from telegram import Update , ReplyKeyboardMarkup , KeyboardButton
from telegram.ext import ContextTypes
class calendarController:

    @staticmethod
    async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("Create Task or Event") , KeyboardButton("Read Task or Event")],
            [KeyboardButton("Update Task or Event") , KeyboardButton("Delete Task or Event")],
            [KeyboardButton("I'm not doing something today")]
        ])
        await update.message.reply_text("Hi! (name of the gmail)\nWhat do you want to do?\nChoose an option " , reply_markup=keyboard)