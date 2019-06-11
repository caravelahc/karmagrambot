from telegram import Bot, Update

from telegram.ext import CommandHandler

from . import analytics


def average_length(bot: Bot, update: Update):
    """Reply the user who invoked the command with hers/his average message length.

    Args:
        bot: The object that represents the Telegram Bot.
        update: The object that represents an incoming update for the bot to handle.

    Returns:
        Doesn't return anything, but reply the user with hers/his respective average length.
    """

    average = analytics.average_message_length(update.message.from_user.id, update.message.chat.id)
    response = f'{average:.3}'

    update.message.reply_text(response)

def karma(bot: Bot, update: Update):
    """Reply the user who invoked the command with hers/his respective karma.

    Args:
        bot: The object that represents the Telegram Bot.
        update: The object that represents an incoming update for the bot to handle.

    Returns:
        Doesn't actually return anything, but answer the user with hers/his respective karma.
    """

    karma = analytics.get_karma(update.message.from_user.id, update.message.chat.id)

    update.message.reply_text(karma)

def devil(bot: Bot, update: Update):
    """Reply the user with some dumb text and the person with the lowest karma, the "devil".

    Args:
        bot: The object that represents the Telegram Bot.
        update: The object that represents an incoming update for the bot to handle.

    Returns:
        Doesn't return, but answer the user with the one with the lowest karma.
    """

    devil = analytics.get_devil_saint(update.message.chat.id)['devil']
    response = f"{devil['first_name']}, there's a special place in hell for you, see you there."

    update.message.reply_text(response)

HANDLERS = [
    CommandHandler('average_length', average_length),
    CommandHandler('karma', karma),
    CommandHandler('devil', devil),
]
