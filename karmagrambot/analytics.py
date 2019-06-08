import dataset

from .config import DB_URI


def average_message_length(user_id, chat_id):
    db = dataset.connect(DB_URI)
    messages = db['messages'].find(user_id=user_id, chat_id=chat_id)
    messages = [m for m in messages if m['length'] is not None]

    if not messages:
        return 0

    return sum(m['length'] for m in messages) / len(messages)

def get_karma(user_id: int, chat_id: int) -> int:
    """Get the karma of an given user in a given chat.

    Args:
        user_id: The id of the user that we want to get the karma.
        chat_id: The id of the chat we're interested in.

    Returns:
        The karma value.
    """

    db = dataset.connect(DB_URI)
    user_messages = db['messages'].find(user_id=user_id, chat_id=chat_id)

    good_karma = 0
    bad_karma = 0
    for message in user_messages:
        replies_to_message = db['messages'].find(replied=message['message_id'])
        for reply in replies_to_message:
            if reply['vote'] == '+':
                good_karma += 1
            elif reply['vote'] == '-':
                bad_karma += 1

    return good_karma - bad_karma