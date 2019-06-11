from telegram import Bot, Update

from telegram.ext import CommandHandler

from . import analytics


def average_length(bot: Bot, update: Update):
    """Reply the user who invoked the command with hers/his average message length.

    Args:
        bot: the object that represents the Telegram Bot.
        update: the object that represents an incoming update for the bot to handle.

    Returns:
        Doesn't return anything, but reply the user with hers/his respective average length.
    """

    average = analytics.average_message_length(update.message.from_user.id, update.message.chat.id)
    response = f'{average:.3}'

    update.message.reply_text(response)

def karma(bot: Bot, update: Update):
    """Reply the user who invoked the command with hers/his respective karma.

    Args:
        bot: the object that represents the Telegram Bot.
        update: the object that represents an incoming update for the bot to handle.

    Returns:
        Doesn't actually return anything, but answer the user with hers/his respective karma.
    """

    karma = analytics.get_karma(update.message.from_user.id, update.message.chat.id)

    update.message.reply_text(karma)

def karmas(bot: Bot, update: Update):
    """Shows the top 10 karmas in a given group, if the groups doesn't have at least 10 users, show the maximum amount

    Args:
        bot: The object that represents the Telegram Bot.
        update: The object that represents an incoming update for the bot to handle.

    Returns:
        Doesn't return anything, but answer the user with the top 10 karmas in the group.
    """

    top_users = analytics.get_top_10_karmas(update.message.chat.id)

    response = ''
    for i in range(len(top_users)):
        response += '{} - {} ({})\n'.format(i + 1, top_users[i]['name'], top_users[i]['karma'])

    update.message.reply_text(response)

HANDLERS = [
    CommandHandler('average_length', average_length),
    CommandHandler('karma', karma),
    CommandHandler('karmas', karmas),
]
