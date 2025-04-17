from aiosqlite import connect

db = None

async def init_db():
    global db
    db = await connect('database.db')
    await db.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        height REAL DEFAULT NULL,
        weight REAL DEFAULT NULL,
        age INTEGER DEFAULT NULL,
        sex REAL DEFAULT NULL,
        goal REAL DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    await db.commit()
    return db

def get_db() -> Connection:
    if db is None:
        raise RuntimeError('Database connection failed.')
    return db
