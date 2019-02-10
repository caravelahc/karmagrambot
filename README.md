# Karmagrambot
Telegram bot that logs messages (not the contents, for the sake of privacy) and votes.

# Configuration
The configuration file is located, by default, at `$XDG_CONFIG_HOME/karmagrambot/config.json`, but if that variable is not set, it falls back to `~/.config/karmagrambot/config.json`.

The expected keys are `token` (required) and `db-path` (optional).

The database is located, by default, at `$XDG_DATA_HOME/karmagrambot/messages.db`, but if that variable is not set, it falls back to `~/.local/share/karmagrambot/messages.db`.
