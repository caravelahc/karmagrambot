import logging

import dataset
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from .commands import HANDLERS
from .config import DB_URI, TOKEN

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
    """Search in the database for an existing vote of the user on the replied message

    Args:
        replied: id of the message which the vote is a reply
        user_id: id of the user who's voting

    Returns:
        The return value. True if the user already voted on the message, False otherwise.
    """
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


def save(_, update):
    db = dataset.connect(DB_URI)
    save_message(update.message, db)
    save_user(update.message.from_user, db)


def track(chat_id, user_id, value, db):
    table = db['tracked']

    if value:
        table.insert(dict(chat_id=chat_id, user_id=user_id))
    else:
        table.delete(chat_id=chat_id, user_id=user_id)


def opt_in(_, update):
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


def opt_out(_, update):
    message = update.message
    chat_id = message.chat_id
    user_id = message.from_user.id

    db = dataset.connect(DB_URI)

    track(chat_id, user_id, False, db)

    message.reply_text('You are no longer being tracked in this chat ;)')


def karma_id_with_message(message):
    target_message = (
        message.reply_to_message if message.reply_to_message is not None else message
    )

    user_id = target_message.from_user.id
    username = target_message.from_user.username

    return user_id, username


def karma_id_with_username(username):
    db = dataset.connect(DB_URI)
    try:
        [user] = db['users'].find(username=username)
    except ValueError:
        return None, username

    user_id = user['user_id']

    return user_id, username


def get_karma(bot, update):
    message = update.message
    text = message.text
    message.from_user.username

    _, *args = text.split()

    user_id, username = (
        karma_id_with_message(message) if not args else karma_id_with_username(args[0])
    )

    if user_id is None:
        message.reply_text(f'Could not find user named {username}')
        return

    karma = analytics.get_karma(user_id, message.chat_id)

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
