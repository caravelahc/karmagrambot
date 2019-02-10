from os import environ
from pathlib import Path
import json


try:
    CONFIG_DIR = Path(environ['XDG_CONFIG_HOME'], __package__)
except KeyError:
    CONFIG_DIR = Path.home() / '.config' / __package__

if not CONFIG_DIR.exists():
    CONFIG_DIR.mkdir()

CONFIG_FILE = CONFIG_DIR / 'config.json'

with open(CONFIG_FILE) as f:
    config = json.load(f)

TOKEN = config['token']

try:
    DB_PATH = Path(config['db-path'])
except KeyError:
    try:
        DB_PATH = Path(environ['XDG_DATA_HOME'], __package__, 'messages.db')
    except KeyError:
        DB_PATH = Path.home() / '.local/share' / __package__ / 'messages.db'

DB_DIR = DB_PATH.parent

if not DB_DIR.exists():
    DB_DIR.mkdir()

DB_URI = f'sqlite:///{DB_PATH}'
