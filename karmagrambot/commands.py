from telegram.ext import CommandHandler

from . import analytics


def average_length(bot: telegram.Bot, update: telegram.Update):
	"""Get the average message length of the user who invoked the command.

	Args:
		bot: the object that represents the Telegram Bot.
		update: the object that represents an incoming update for the bot to handle.

	Returns:
		Doesn't return anything, but reply the user with hers/his respective average length.
	"""

    average = analytics.average_message_length(update.message.from_user.id, update.message.chat.id)
    response = f'{average:.3}'

    update.message.reply_text(response)

def karma(bot: telegram.Bot, update: telegram.Update):
	"""Get the karma of the user who invoked the command.

	Args:
		bot: the object that represents the Telegram Bot.
		update: the object that represents an incoming update for the bot to handle.

	Returns:
		Doesn't actually return anything, but answer the user with hers/his respective karma.
	"""

	karma = analytics.get_karma(update.message.from_user.id, update.message.chat.id)

	update.message.reply_text(karma)

HANDLERS = [
    CommandHandler('average_length', average_length),
    CommandHandler('karma', karma),
]
