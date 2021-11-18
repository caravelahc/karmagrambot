"""Utility module."""
from calendar import monthrange
from contextlib import contextmanager
from datetime import date
from typing import Iterator, NamedTuple, Optional

import dataset

from telegram import Message


class UserInfo(NamedTuple):
    """Utility class to aggregate user information."""

    user_id: int
    username: str


def user_info_from_message_or_reply(message: Message) -> UserInfo:
    """Get user info from either a message or the message replied by it.

    If the message is a reply, user info will refer to the user that sent
    the message being replied to. Else, it will refer to the message itself.

    Args:
        message: The message to be analysed.

    Returns:
        The information on the target message.
    """
    target_message = (
        message.reply_to_message if message.reply_to_message is not None else message
    )

    user_id = target_message.from_user.id
    username = target_message.from_user.username

    return UserInfo(user_id, username)


def user_info_from_username(db, username) -> Optional[UserInfo]:
    """Get user info from our database based on a username.

    Args:
        db: The database.
        username: The username to search for.

    Returns:
        The information on the user, if found.
    """
    try:
        [user] = db['users'].find(username=username)
    except ValueError:
        return None

    user_id = user['user_id']

    return UserInfo(user_id, username)


def get_period(arg_period: str) -> Optional[date]:
    today = date.today()
    if arg_period in ('m', 'month'):
        timestamp = today.replace(day=1)
    elif arg_period in ('y', 'year'):
        timestamp = today.replace(day=1, month=1)
    elif arg_period in ('w', 'week'):
        last_month = today.month
        days_last_month = monthrange(today.year, today.month)[1]
        timestamp = today.replace(
            day=(today.day - 7) % days_last_month, month=last_month
        )
    else:
        return None

    return timestamp


@contextmanager
def open_database(uri: str) -> Iterator[dataset.Database]:
    db = dataset.connect(uri)
    yield db
    db.close()
