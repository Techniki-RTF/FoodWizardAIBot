import os
from aiosqlite import connect, Connection

db: Connection | None = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "../database")
os.makedirs(DB_DIR, exist_ok=True)

async def init_db():
    global db
    db = await connect(os.path.join(DB_DIR, 'database.db'))
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

async def create_user(uid):
    c_db = get_db()
    await c_db.execute('''
            INSERT OR IGNORE INTO users (user_id)
            VALUES (?)
            ''', (uid,))
    await c_db.commit()

async def change_goal(uid, goal):
    c_db = get_db()
    await c_db.execute('UPDATE users SET goal = ? WHERE user_id = ?', (goal, uid))
    await c_db.commit()

async def change_user_sex(uid, sex):
    c_db = get_db()
    await c_db.execute('UPDATE users SET sex = ? WHERE user_id = ?', (sex, uid))
    await c_db.commit()

async def get_profile(uid):
    c_db = get_db()
    cursor = await c_db.execute('SELECT height, weight, age, sex, goal FROM users WHERE user_id = ?', (uid,))
    row = await cursor.fetchone()
    if row:
        height, weight, age, sex, goal = row
        if age: age = int(age)
    else:
        height = weight = age = sex = goal = None
    profile = {'height': height, 'weight': weight, 'age': age, 'sex': sex, 'goal': goal}
    return profile

async def change_param(uid, param, value):
    c_db = get_db()
    await c_db.execute(f'UPDATE users SET {param.replace('c_', '', 1)} = ? WHERE user_id = ?', (value, uid))
    await c_db.commit()