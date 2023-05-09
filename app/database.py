import sqlite3 as sq

db = sq.connect('tg.db')
cur = db.cursor()

async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS accounts("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tg_id INTEGER, "
                "cart_id TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS items("
                "i_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "id INTEGER REFERENCES accounts, "
                "url TEXT, "
                "brand TEXT)")
    db.commit()


async def cmd_start_db(user_id):
    user = cur.execute("SELECT * FROM accounts WHERE tg_id == {key}".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO accounts (tg_id) VALUES ({key})".format(key=user_id))
        db.commit()


async def add_item(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO items (id, url, brand) VALUES (?, ?, ?)",
                    (data['id'], data['url'], data['type']))
        db.commit()


async def select_news_item():
    return cur.execute("SELECT (url) FROM items JOIN accounts ON items.id = accounts.id").fetchall()


async def select_user_id(user_id):
    return cur.execute("SELECT (id) FROM accounts WHERE tg_id == {key}".format(key=user_id)).fetchone()
    
async def all_users_id():
    return cur.execute("SELECT (tg_id) FROM accounts").fetchall()