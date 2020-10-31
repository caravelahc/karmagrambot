# Karmagrambot
Telegram bot that logs messages (not the contents, for the sake of privacy) and votes.

# Installing
You can either use an application such as [pipx](https://github.com/pipxproject/pipx) (recommended) or just `pip`:
```shell
~ $ pipx install git+https://github.com/caravelahc/karmagrambot
```

# Running
1. You must create a Telegram bot with [the Botfather](https://t.me/botfather) in order to get a token.
2. Create a configuration file as explained below, containing at least the token.
3. Run `karmagrambot`.

# Configuration
The configuration file is located, by default, at `$XDG_CONFIG_HOME/karmagrambot/config.json`, but if that variable is not set, it falls back to `~/.config/karmagrambot/config.json`.

The expected keys are `token` (required) and `db-path` (optional).

The database is located, by default, at `$XDG_DATA_HOME/karmagrambot/messages.db`, but if that variable is not set, it falls back to `~/.local/share/karmagrambot/messages.db`.
