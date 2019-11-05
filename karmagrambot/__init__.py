import dataset
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from .config import TOKEN, DB_URI
from .commands import HANDLERS

logging.basicConfig()


def check_message(message: str) -> bool:
    ''' Check if the message is composed only by -'s or + 's.

    Args:
        message: message received from the user

    Returns:
        The return value + if the message is only +, - if the message is only -, and None otherwise
    '''
    if all(x == '-' for x in message):
        return '-'
    elif all(c == '+' for c in message):
        return '+'

    return None


def already_voted(replied: str, user_id: str, db: dataset.Database) -> bool:
    '''Search in the database for an existing vote of the user on the replied message

    Args:
        replied: id of the message which the vote is a reply
        user_id: id of the user who's voting

    Returns:
        The return value. True if the user already voted on the message, False otherwise.
    '''
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

    vote = check_message(message.text)

    if vote is not None and already_voted(replied, message.from_user.id, db):
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

def get_karma(bot, update):
    message = update.message
    chat_id = message.chat_id
    user_id = message.from_user.id
    text = message.text
    username = f'@{message.from_user.username}'

    if message.reply_to_message is not None:
        user_id = message.reply_to_message.from_user.id
        username = f'@{message.reply_to_message.from_user.username}'
    
    if len(text.split()) > 1:
        username_from_msg = text.split()[1]
        db = dataset.connect(DB_URI)
        users = db['users'].find(username=username_from_msg[1:]) #[1:] to remove the preceding @ from username
        for user in users:
            user_id = user['user_id']
            username=f'{username_from_msg}'
            print(user_id)
        if username != username_from_msg:
            message.reply_text(f'{username_from_msg} is not in the database for this chat')
            return

    karma = analytics.get_karma(user_id, chat_id)
    message.reply_text(f'{username} has {karma} karma in this chat')


def run():
    updater = Updater(TOKEN)

    handlers = HANDLERS + [
        CommandHandler('opt_in', opt_in),
        CommandHandler('opt_out', opt_out),
        CommandHandler('get_karma', get_karma),
        MessageHandler(Filters.all, save),  # must be last
    ]

    for h in handlers:
        updater.dispatcher.add_handler(h)

    updater.start_polling()
    updater.idle()
