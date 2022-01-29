from threading import Thread
import time
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackContext)
import os
from Data_source import DataSource
import datetime

TOKEN = os.getenv('TOKEN')
DS_URL = "postgres://udemy_telegram_user:password@localhost:5432/udemy_telegram"
message_DS = DataSource(DS_URL)


class TestBot101:

    def __init__(self) -> None:
        self.keyboard = [[KeyboardButton('Add remainder'), KeyboardButton('Add dude'), KeyboardButton('Add No')],
                         [KeyboardButton('Add re'), KeyboardButton('Add dud'), KeyboardButton('Add N')],
                         [KeyboardButton('Add rem'), KeyboardButton('Add du'), KeyboardButton('Add')]]
        self.thread = Thread(target=self.check_reminders, args=(), daemon=True)

    def start_handler(self, update):
        update.message.reply_text("hi creator", reply_markup=self.keyboard_replier())

    def add_reminder_handler(self, update: Update,):
        update.message.reply_text("What should I remind you about?")
        return ENTER_MESSAGE

    def enter_message_handler(self, update: Update, context: CallbackContext):
        update.message.reply_text("When should I remind you ? ('day/month/Year Hour:Minute')")
        context.user_data["message_text"] = update.message.text
        return ENTER_TIME
    
    def enter_time_handler(self, update: Update, context: CallbackContext):
        message_text = context.user_data["message_text"]
        time = datetime.datetime.strptime(update.message.text, "%d/%m/%Y %H:%M")
        message_data = message_DS.create_reminder(
            chat_id=update.message.chat_id,
            message=message_text,
            time=time
        )
        update.message.reply_text(f"Your Reminder ({message_data.__repr__()}) Have been Set!")
        return ConversationHandler.END

    def keyboard_replier(self):
        return ReplyKeyboardMarkup(self.keyboard)
    
    def check_reminders(self):
        while True:
            for reminder_data in message_DS.get_all_reminders():
                if reminder_data.should_be_fired():
                    message_DS.fire_reminder(reminder_data.reminder_id)
                    updater.bot.send_message(reminder_data.chat_id, "It's time to : " + reminder_data.message)
            time.sleep(3)       
    
    def start_check_reminders_task(self):
        self.thread.start()


ENTER_MESSAGE, ENTER_TIME = range(2)

if __name__ == "__main__":
    Bot = TestBot101()
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", Bot.start_handler))
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Add remainder'), Bot.add_reminder_handler)],
        states={
            ENTER_MESSAGE: [MessageHandler(Filters.all, Bot.enter_message_handler)],
            ENTER_TIME: [MessageHandler(Filters.all, Bot.enter_time_handler)]
        },      
        fallbacks=[]
        )
    )
    message_DS.create_tables()
    updater.start_polling()
    Bot.start_check_reminders_task()
