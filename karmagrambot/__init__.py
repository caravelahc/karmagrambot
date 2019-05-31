import dataset
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from .config import TOKEN, DB_URI
from .commands import HANDLERS

logging.basicConfig()

def already_voted(replied, user_id):
    table = db['tracked']
    row = table.find_one(replied=replied, user_id=user_id)
    return row is not None

def is_tracked(chat_id, user_id, db):
    table = db['tracked']
    row = table.find_one(chat_id=chat_id, user_id=user_id)
    return row is not None

def save_message(message, db):
    if not is_tracked(message.chat_id, message.from_user.id, db):
        return

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

    if vote is not None and already_voted(replied, message.from_user.id):
        return

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

    table.upsert(new_row, keys=['user_id'])


def save(bot, update):
    db = dataset.connect(DB_URI)
    save_message(update.message, db)
    save_user(update.message.from_user, db)


def track(chat_id, user_id, value, db):
    table = db['tracked']

    if value:
        table.insert(dict(chat_id=chat_id, user_id=user_id))
    else:
        table.delete(chat_id=chat_id, user_id=user_id)


def opt_in(bot, update):
    message = update.message
    chat_id = message.chat_id
    user_id = message.from_user.id

    db = dataset.connect(DB_URI)

    track(chat_id, user_id, True, db)

    message.reply_text(
        'You are now being tracked in this chat. '
        'Worry not, the contents of your messages are not saved, '
        'only their length ;)'
    )


def opt_out(bot, update):
    message = update.message
    chat_id = message.chat_id
    user_id = message.from_user.id

    db = dataset.connect(DB_URI)

    track(chat_id, user_id, False, db)

    message.reply_text('You are no longer being tracked in this chat ;)')


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
