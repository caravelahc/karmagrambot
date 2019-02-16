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

    length = None
    if message.text is not None:
        length = len(message.text)
    elif message.caption is not None:
        length = len(message.caption)

    vote = None
    if message.text == '+':
        vote = '+'
    elif message.text == '-':
        vote = '-'

    new_row = {
        'timestamp': message.date,
        'message_id': message.message_id,
        'chat_id': message.chat_id,
        'user_id': message.from_user.id,
        'replied': replied,
        'length': length,
        'vote': vote,
    }

    db['messages'].upsert(new_row, keys=['message_id', 'chat_id'])


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

    handlers = HANDLERS + [
        MessageHandler(Filters.all, save),  # must be last
    ]

    for h in handlers:
        updater.dispatcher.add_handler(h)

    updater.start_polling()
    updater.idle()
