# Adding a new command

1. Fork this repository (button at the top left corner);
2. Clone your fork;
3. Create a separate branch for your new feature with `git checkout -b <branch-name>`;
4. Implement the query and logic in the `analytics.py` file, following the model;
5. Create a command in `commands.py` and a respective `CommandHandler`, adding it to the `HANDLERS` list, following the model;
6. Commit your changes to your branch, push it to GitHub and open a PR.


# Database schema

## `messages`
- `message_id`: the ID of the message, specific to the chat where it was sent;
- `chat_id`: the ID of the chat where the message was sent;
- `user_id`: the ID of the user who sent the message;
- `replied`: the ID of the message for which this one is a reply (`null`, if it isn't a reply);
- `length`: the length of the text contents in characters;
- `vote`: `'+'` or `'-'` if the text contents of the message are just that, and `null` otherwise.

Please note that forwarded messages count as new messages. The user who forwarded it is the user who effectively sent it. Neither the original message nor the original sender are tracked.

## `users`
The fields are `user_id`, `first_name`, `last_name`, and `username`. No further description seems necessary.


# Library documentation

- To implement a new query, refer to [`dataset`'s documentation](https://dataset.readthedocs.io/en/latest/quickstart.html#reading-data-from-tables);

- To implement a new command, refer to [`python-telegram-bot`'s documentation](https://python-telegram-bot.readthedocs.io/en/stable/telegram.update.html).


# In need of any additional help, feel free to contact me [on Telegram](https://t.me/cauebs)
