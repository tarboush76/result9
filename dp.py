import sqlite3
from contextlib import closing

DB_PATH = 'bot.db'

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

SCHEMA = r'''
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  first_name TEXT,
  last_name TEXT,
  username TEXT
);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  text TEXT,
  date INTEGER,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
'''

def init_db():
    with closing(get_conn()) as conn:
        c = conn.cursor()
        c.executescript(SCHEMA)
        conn.commit()
