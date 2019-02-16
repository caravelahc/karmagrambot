from telegram.ext import CommandHandler

from .analytics import average_message_length


def average_length(bot, update):
    message = update.message
    user_id = message.from_user.id
    chat_id = message.chat.id

    average = average_message_length(user_id, chat_id)
    message.reply_text(f'{average:.3}')


HANDLERS = [
    CommandHandler('average_length', average_length)
]
