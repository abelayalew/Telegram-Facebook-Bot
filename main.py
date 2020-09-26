import sys, os
from decouple import config
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from facebook_scraper import get_posts
import threading, time

# django setup
sys.dont_write_bytecode = True
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import django
django.setup()
from commands import Add, Help, List, Remove, Start
import post_handler
from db.models import *

# tokens
TOKEN = config('TOKEN')


class FbPage:
    def __init__(self):
        self.updater = Updater(token=TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def start_bot(self):
        """
        start the bot
        :return: None
        """
        self.start_time = time.time()
        self.dispatcher.add_handler(MessageHandler(Filters.command, self.command_handler))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.text_handler))
        self.dispatcher.add_handler(CallbackQueryHandler(Remove.callbacks))
        self.updater.start_polling()
        threading.Thread(target=post_handler.post_threader).start()
        print("Initialized")

    def extract_message(self, update):
        chat_id = update.message.chat_id
        first_name = update.message.chat.first_name
        last_name = update.message.chat.last_name
        username = update.message.chat.username
        message = update.message.text
        message_id = update.message.message_id
        print(chat_id, first_name, last_name, username, message, message_id)
        return chat_id, first_name, last_name, username, message, message_id

    def command_handler(self, update, context) -> None:
        """
        a method to handle all commands
        :param update:
        :param context:
        :return: None
        """
        command = update.message.text.split(' ')[0]
        supported_commands = {
            '/start': Start.command_start,
            '/add': Add.command_add,
            '/help': Help.command_help,
            '/list': List.command_list,
            '/remove': Remove.command_remove
        }
        if command in supported_commands:
            print(command)
            supported_commands[command](update, context, *self.extract_message(update))

    def text_handler(self, update, context):
        """
        https://www.facebook.com/pagename/adss
        https://m.facebook.com/pagename/adss

        :param update:
        :param context:
        :return:
        """
        data = list(self.extract_message(update))
        text = update.message.text
        if 'facebook.com' in text:
            try:
                page = text.split('facebook.com')[1].split('/')[1]
                list(get_posts(page, pages=1))
                data.append(page)
                Add.command_add(update, context, *tuple(data))
                return
            except:
                update.message.reply_text("Invalid Link or Can't Add That Page.")
                return
        update.message.reply_text("Unrecognized Text")


bot = FbPage()
bot.start_bot()
