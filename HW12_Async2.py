DB_NAME = 'quiz_bot.db'
import aiosqlite

async def get_quiz_index(user_id):
  async with aiosqlite.connect(DB_NAME) as db:
    async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
      results = await cursor.fetchone()
      if results is not None:
        return results[0]
      else:
        return 0
      
async def get_score(user_id):
  async with aiosqlite.connect(DB_NAME) as db:
    async with db.execute('SELECT right_answers FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
      results = await cursor.fetchone()
      if results is not None:
        return results[0]
      else:
        return 0

async def update_quiz_index(user_id, index, right):
  async with aiosqlite.connect(DB_NAME) as db:
    await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, right_answers) VALUES (?, ?, ?)', (user_id, index, right))
    await db.commit()

async def create_table():
  async with aiosqlite.connect(DB_NAME) as db:
    await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, right_answers INTEGER)''')
    await db.commit()