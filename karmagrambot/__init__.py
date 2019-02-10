import dataset
import logging

from telegram.ext import Updater, MessageHandler, Filters

from .config import TOKEN, DB_URI
from .commands import HANDLERS

logging.basicConfig()


def save_message(message, db):
    replied = None
    if message.reply_to_message is not None:
        replied = message.reply_to_message.message_id

    vote = None
    if message.text == '+':
        vote = '+'
    elif message.text == '-':
        vote = '-'

    row = {
        'message_id': message.message_id,
        'chat_id': message.chat_id,
        'user_id': message.from_user.id,
        'replied': replied,
        'length': len(message.text),
        'vote': vote,
    }

    db['messages'].insert(row)


def save_user(user, db):
    row = {
        'user_id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
    }

    db['users'].upsert(row, keys=['user_id'])


def save(bot, update):
    db = dataset.connect(DB_URI)
    save_message(update.message, db)
    save_user(update.message.from_user, db)


def run():
    updater = Updater(TOKEN)
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text, save)
    )

    for handler in HANDLERS:
        updater.dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()
