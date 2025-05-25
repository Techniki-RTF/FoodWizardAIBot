import os
from aiosqlite import connect, Connection

db: Connection | None = None

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database"))
os.makedirs(DB_DIR, exist_ok=True)

async def init_db():
        global db
        db = await connect(os.path.join(DB_DIR, 'database.db'))

        await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT
        )
        ''')

        columns = {
            "height": "REAL DEFAULT NULL",
            "weight": "REAL DEFAULT NULL",
            "age": "INTEGER DEFAULT NULL",
            "sex": "TEXT DEFAULT NULL",
            "goal": "TEXT DEFAULT NULL",
            "activity": "INTEGER DEFAULT NULL",
            "daily_kcal": "INTEGER DEFAULT NULL",
            "bmi": "TEXT DEFAULT 0",
            "lang": "TEXT DEFAULT NULL",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }

        cursor = await db.execute("PRAGMA table_info(users)")
        existing_columns = [row[1] async for row in cursor]

        for col_name, col_type in columns.items():
            if col_name not in existing_columns:
                await db.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")

        await db.commit()
        return db

async def get_db() -> Connection:
    if db is None:
        raise RuntimeError('Database connection failed.')
    return db

async def create_user(uid):
    c_db = await get_db()
    await c_db.execute('''
            INSERT OR IGNORE INTO users (user_id)
            VALUES (?)
            ''', (uid,))
    await c_db.commit()
    
async def get_user_lang(uid):
    c_db = await get_db()
    cursor = await c_db.execute('SELECT lang FROM users WHERE user_id = ?', (uid,))
    row = await cursor.fetchone()
    lang = row[0] if row else None
    return lang

async def change_user_lang(uid, lang):
    c_db = await get_db()
    await c_db.execute('UPDATE users SET lang = ? WHERE user_id = ?', (lang, uid))
    await c_db.commit()

async def change_goal(uid, goal):
    c_db = await get_db()
    await c_db.execute('UPDATE users SET goal = ? WHERE user_id = ?', (goal, uid))
    await c_db.commit()

async def change_user_sex(uid, sex):
    c_db = await get_db()
    await c_db.execute('UPDATE users SET sex = ? WHERE user_id = ?', (sex, uid))
    await c_db.commit()

async def get_profile(uid):
    c_db = await get_db()
    cursor = await c_db.execute('SELECT height, weight, age, sex, goal, bmi, activity, daily_kcal FROM users WHERE user_id = ?', (uid,))
    row = await cursor.fetchone()
    if row:
        height, weight, age, sex, goal, bmi, activity, daily_kcal = row
        if age: age = int(age)
    else:
        height = weight = age = sex = goal = bmi = activity = daily_kcal = None
    profile = {'height': height, 'weight': weight, 'age': age, 'sex': sex, 'goal': goal, 'bmi': bmi, 'activity': activity, 'daily_kcal': daily_kcal}
    return profile

async def change_param(uid, param, value):
    c_db = await get_db()
    await c_db.execute(f'UPDATE users SET {param.replace('c_', '', 1)} = ? WHERE user_id = ?', (value, uid))
    cursor = await c_db.execute('SELECT height, weight FROM users WHERE user_id = ?', (uid,))
    row = await cursor.fetchone()
    if row:
        height, weight = row
        if not(height and weight): pass
        else:
            bmi = "%.1f" % (weight / (height / 100) ** 2)
            await c_db.execute(f'UPDATE users SET bmi = ? WHERE user_id = ?', (bmi, uid))
    await c_db.commit()

async def change_activity(uid, activity):
    c_db = await get_db()
    await c_db.execute('UPDATE users SET activity = ? WHERE user_id = ?', (activity, uid))
    await c_db.commit()

async def change_daily_kcal(uid, kcal):
    c_db = await get_db()
    await c_db.execute('UPDATE users SET daily_kcal = ? WHERE user_id = ?', (kcal, uid))
    await c_db.commit()
