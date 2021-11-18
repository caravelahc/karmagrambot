import logging
from dataclasses import dataclass
from typing import Optional, Tuple

import dataset
from telegram import Message
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from .commands import HANDLERS
from .config import DB_URI, TOKEN

logging.basicConfig()


@dataclass(frozen=True)
class MessageInfo:
    replied: Optional[int] = None
    length: Optional[int] = None
    vote: Optional[str] = None


def get_vote(message: str) -> Optional[str]:
    """Check if the message is composed only by -'s or + 's.

    Args:
        message: message received from the user

    Returns:
        The return value + if the message is only +, - if the message is only -, and None otherwise
    """
    if all(x == '-' for x in message):
        return '-'

    if all(c == '+' for c in message):
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
    table = db['messages']
    row = table.find_one(replied=replied, user_id=user_id)
    return row is not None


def is_tracked(chat_id, user_id, db):
    table = db['tracked']
    row = table.find_one(chat_id=chat_id, user_id=user_id)
    return row is not None


def get_message_text(message: Message) -> Optional[str]:
    if message.text is not None:
        return message.text

    if message.caption is not None:
        return message.caption

    return None

def get_message_info(message: Message) -> MessageInfo:
    replied = (
        message.reply_to_message.message_id
        if message.reply_to_message is not None
        else None
    )

    text = get_message_text(message)

    if text is None:
        return MessageInfo(replied=replied)

    length = len(text)
    vote = get_vote(text)

    return MessageInfo(
        replied=replied,
        length=length,
        vote=vote
    )


def save_message(message, db):
    if not is_tracked(message.chat_id, message.from_user.id, db):
        return

    message_info = get_message_info(message)

    def get_valid_vote() -> Optional[str]:
        vote = message_info.vote

        if vote is None:
            return None

        if already_voted(message_info.replied, message.from_user.id, db):
            return None

        return vote

    new_row = {
        'timestamp': message.date,
        'message_id': message.message_id,
        'chat_id': message.chat_id,
        'user_id': message.from_user.id,
        'replied': message_info.replied,
        'length': message_info.length,
        'vote': get_valid_vote(),
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
    db.close()


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

    if is_tracked(chat_id, user_id, db):
        message.reply_text(u'You are already being tracked in this chat \U0001F600')
        return

    track(chat_id, user_id, True, db)

    db.close()

    message.reply_text(
        u'You are now being tracked in this chat. '
        'Worry not, the contents of your messages are not saved, '
        'only their length \U00002713'
    )


def opt_out(_, update):
    message = update.message
    chat_id = message.chat_id
    user_id = message.from_user.id

    db = dataset.connect(DB_URI)

    if not is_tracked(chat_id, user_id, db):
        message.reply_text(u'You are not being tracked in this chat \U0001F914')
        return

    track(chat_id, user_id, False, db)

    db.close()

    message.reply_text(u'You are no longer being tracked in this chat \U0001F64B')

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
