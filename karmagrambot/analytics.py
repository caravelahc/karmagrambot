import dataset

from .config import DB_URI

from .types import UserKarma, DevilSaint

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

def get_devil_saint(chat_id: int) -> dict:
    """Get the users with the lowest and the greatest karma in a given chat.

    Args:
        chat_id: The id of the chat that we'll be searching in.

    Returns:
        A dictionary with the informations of both devil and saint.
    """

    db = dataset.connect(DB_URI)
    users = db['tracked'].find(chat_id=chat_id)
    user_ids = [u['user_id'] for u in users]

    devil_id = sorted(user_ids, key=lambda u: get_karma(u, chat_id))[0]
    saint_id = user_ids[-1]

    devil = db['users'].find_one(user_id=devil_id)
    saint = db['users'].find_one(user_id=saint_id)

    devil_saint = DevilSaint(UserKarma(user_name(*devil), get_karma(devil_id, chat_id)), UserKarma(user_name(*saint), get_karma(saint_id, chat_id)))

    return devil_saint