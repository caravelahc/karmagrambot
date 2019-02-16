import dataset
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

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
    table = db['users']

    new_row = {
        'user_id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
    }

    if table.find_one(user_id=user.id) is None:
        new_row['tracked'] = True
        table.insert(new_row)
    else:
        table.update(new_row, keys=['user_id'])


def save(bot, update):
    db = dataset.connect(DB_URI)
    save_message(update.message, db)
    save_user(update.message.from_user, db)


def track(user_id, value):
    db = dataset.connect(DB_URI)
    table = db['users']

    new_row = {
        'user_id': user_id,
        'tracked': value,
    }

    table.upsert(new_row, keys=['user_id'])


def opt_in(bot, update):
    track(update.message.from_user.id, True)


def opt_out(bot, update):
    track(update.message.from_user.id, False)


def run():
    updater = Updater(TOKEN)

    handlers = HANDLERS + [
        CommandHandler('opt_in', opt_in),
        CommandHandler('opt_out', opt_out),
        MessageHandler(Filters.all, save),  # must be last
    ]

    for h in handlers:
        updater.dispatcher.add_handler(h)

    updater.start_polling()
    updater.idle()
