import dataset

from .config import DB_URI


def open_db():
    return dataset.connect(DB_URI)


def average_message_length(user_id, chat_id):
    db = open_db()

    messages = db['messages'].find(user_id=user_id, chat_id=chat_id)
    messages = [m for m in messages if m['length'] is not None]

    return sum(m['length'] for m in messages) / len(messages)


def count_votes(chat_id, vote, limit=10):
    db = open_db()

    return db.query(
        '''
        SELECT original.user_id, COUNT(reply.vote) AS votes
        FROM messages original
        JOIN messages reply
            ON original.message_id = reply.replied
        WHERE
            original.chat_id = ? AND
            reply.vote = ?
        GROUP BY user_id
        ORDER BY votes
        LIMIT ?
        ''',
        chat_id,
        vote,
        limit
    )


def most_upvoted(chat_id):
    return count_votes(chat_id, '+')


def most_downvoted(chat_id):
    return count_votes(chat_id, '-')
