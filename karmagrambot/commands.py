"""Aggregate every user-available command."""
from telegram import Bot, Update
from telegram.ext import CommandHandler

import dataset

from . import analytics
from .config import DB_URI
from .util import user_info_from_message_or_reply, user_info_from_username


def average_length(_: Bot, update: Update):
    """Reply the user who invoked the command with hers/his average message length.

    Args:
        bot: The object that represents the Telegram Bot.
        update: The object that represents an incoming update for the bot to handle.
    """

    average = analytics.average_message_length(
        update.message.from_user.id, update.message.chat.id
    )
    response = f'{average:.3}'

    update.message.reply_text(response)


def karma(_: Bot, update: Update):
    """Reply the user who invoked the command with hers/his respective karma.

    Args:
        bot: The object that represents the Telegram Bot.
        update: The object that represents an incoming update for the bot to handle.
    """
    db = dataset.connect(DB_URI)

    message = update.message
    text = message.text

    _, *args = text.split()

    username = args[0].lstrip('@') if args else None

    user_info = (
        user_info_from_message_or_reply(message)
        if username is None
        else user_info_from_username(db, username)
    )

    if user_info is None:
        message.reply_text(f'Could not find user named {username}')
        return

    user_karma = analytics.get_karma(user_info.user_id, message.chat_id)

    message.reply_text(f'{user_info.username} has {user_karma} karma in this chat')


def karmas(_: Bot, update: Update):
    """Shows the top 10 karmas in a given group.

    If the group doesn't have at least 10 users, shows as many as there are in
    the group.

    Args:
        bot: The object that represents the Telegram Bot.
        update: The object that represents an incoming update for the bot to handle.
    """
    top_users = analytics.get_top_n_karmas(update.message.chat.id, 10)

    response = '\n'.join(
        f'{i} - {user.name} ({user.karma})' for i, user in enumerate(top_users, 1)
    )

    update.message.reply_text(response)


def devil(_: Bot, update: Update):
    """Reply the user with some dumb text and the person with the lowest karma, the "devil".

    Args:
        bot: The object that represents the Telegram Bot.
        update: The object that represents an incoming update for the bot to handle.
    """
    group_devil = analytics.get_devil_saint(update.message.chat.id).devil
    response = f"{group_devil.name}, there's a special place in hell for you, see you there."

    update.message.reply_text(response)


def saint(_: Bot, update: Update):
    """Reply the user with a message and the person with the highest karma, the "saint".

    Args:
        bot: The object that represents the Telegram Bot.
        update: The object that represents an incoming update for the bot to handle.
    """
    group_saint = analytics.get_devil_saint(update.message.chat.id).saint
    response = f"{group_saint.name}, apparently you're the nicest person here. I don't like you."

    update.message.reply_text(response)


HANDLERS = [
    CommandHandler('average_length', average_length),
    CommandHandler('karma', karma),
    CommandHandler('karmas', karmas),
    CommandHandler('devil', devil),
    CommandHandler('saint', saint),
]
