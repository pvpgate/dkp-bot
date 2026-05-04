import sqlite3

conn = sqlite3.connect("dkp.db")
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        public_id INTEGER UNIQUE,
        name TEXT,
        owner_id INTEGER,
        owner_name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clan_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        clan_id INTEGER,
        status TEXT DEFAULT 'pending'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clan_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        clan_id INTEGER,
        role TEXT DEFAULT 'member',
        dkp INTEGER DEFAULT 0
    )
    """)

    conn.commit()