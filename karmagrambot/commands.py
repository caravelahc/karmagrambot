from telegram.ext import CommandHandler

from .analytics import average_message_length


def average_length(bot, update):
    message = update.message
    user_id = message.from_user.id

    response = f'{average_message_length(user_id):.3}'
    message.reply_text(response)


HANDLERS = [
    CommandHandler('average_length', average_length)
]
