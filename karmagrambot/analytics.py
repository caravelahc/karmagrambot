import dataset

from .config import DB_URI


def average_message_length(user_id):
    db = dataset.connect(DB_URI)
    messages = db['messages'].find(user_id=user_id)
    messages = list(messages)  # because otherwise results are read lazily

    return sum(m['length'] for m in messages) / len(messages)
