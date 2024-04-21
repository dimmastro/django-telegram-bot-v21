import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dtb.settings')
django.setup()

from telegram import Bot
from telegram.ext import Updater

from dtb.settings import TELEGRAM_TOKEN
from tgbot.dispatcher import setup_dispatcher
# from tgbot.dispatcher import main


from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
#

def run_polling(tg_token: str = TELEGRAM_TOKEN):
    """ Run bot in polling mode """
    # updater = Updater(tg_token, use_context=True)

    # dp = updater.dispatcher
    application = Application.builder().token(tg_token).build()
    application = setup_dispatcher(application)
    # application = setup_dispatcher()

    # bot_info = Bot(tg_token).get_me()
    # bot_link = f"https://t.me/{bot_info['username']}"

    # print(f"Polling of '{bot_link}' has started")
    # it is really useful to send '👋' emoji to developer
    # when you run local test
    # bot.send_message(text='👋', chat_id=<YOUR TELEGRAM ID>)

    # updater.start_polling()
    # updater.idle()

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    run_polling()
    pass

# run_polling()