from telegram.ext import CommandHandler

import analytics


def average_length(bot, update):
    message = update.message
    user_id = message.from_user.id
    chat_id = message.chat.id

    average = analytics.average_message_length(user_id, chat_id)
    response = f'{average:.3}'

    message.reply_text(response)

def karma(bot, update):
	message = update.message
	user_id = message.from_user.id
	chat_id = message.chat.id

	karma = analytics.get_karma(user_id, chat_id)
	response = f'{karma}'

	message.reply_text(response)

HANDLERS = [
    CommandHandler('average_length', average_length),
    CommandHandler('karma', karma),
]
