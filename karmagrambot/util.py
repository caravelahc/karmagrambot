"""Utility module."""
from typing import NamedTuple, Optional

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
        message.reply_to_message
        if message.reply_to_message is not None
        else message
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
