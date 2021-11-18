"""Aggregate every user-available command."""
from textwrap import dedent

from telegram import Bot, Update
from telegram.ext import CommandHandler

from . import analytics
from .config import DB_URI
from .util import (
    get_period,
    user_info_from_message_or_reply,
    user_info_from_username,
    open_database,
)


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
    message = update.message
    text = message.text

    _, *args = text.split()

    username = None
    period = get_period('m')
    if args:
        for arg in args:
            arg = arg.lstrip('-')
            if arg in ('w', 'week', 'y', 'year', 'all', 'alltime'):
                period = get_period(arg)
            elif arg != 'm':
                username = arg.lstrip('@')

    with open_database(DB_URI) as db:
        user_info = (
            user_info_from_message_or_reply(message)
            if username is None
            else user_info_from_username(db, username)
        )

    if user_info is None:
        message.reply_text(f'Could not find user named {username}')
        return

    user_karma = analytics.get_karma(user_info.user_id, message.chat_id, period)

    period_suffix = f'(since {period})' if period is not None else f'(all time)'
    message.reply_text(f'{user_info.username} has {user_karma} karma in this chat {period_suffix}.')


def karmas(_: Bot, update: Update):
    """Shows the top 10 karmas in a given group.

    If the group doesn't have at least 10 users, shows as many as there are in
    the group.

    Args:
        bot: The object that represents the Telegram Bot.
        update: The object that represents an incoming update for the bot to handle.
    """
    text = update.message.text
    _, *args = text.split()
    arg = args[0] if args else 'm'
    requested_period = arg.lstrip('-')
    if requested_period not in ('m', 'month', 'w', 'week', 'y', 'year', 'all', 'alltime'):
        update.message.reply_text(f'Period {requested_period} is not supported.')
        return

    period = get_period(arg)

    top_users = analytics.get_top_n_karmas(update.message.chat.id, 10, period)

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

def help_message(_: Bot, update: Update):
    """Shows the commands that can be used with the bot.

    Args:
        bot: The object that represents the Telegram Bot.
        update: The object that represents an incoming update for the bot to handle.
    """

    response = dedent(f"""
                Karma is obtained through replying messages with one or more + or -.

                The following commands are available:

                /average_length - informs your average message length.
                /karma - informs your respective karma.
                /karmas - shows the top 10 karmas in a given group.
                /devil - replies the user informing who is the person with the lowest karma.
                /saint - replies the user informing who is the person with the highest karma.
                """)

    update.message.reply_text(response)


HANDLERS = [
    CommandHandler('average_length', average_length),
    CommandHandler('karma', karma),
    CommandHandler('karmas', karmas),
    CommandHandler('devil', devil),
    CommandHandler('saint', saint),
    CommandHandler('help', help_message),
]
