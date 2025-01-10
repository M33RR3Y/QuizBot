import aiosqlite
from config import DB_NAME


## Создаём 2 таблицы quiz_state и quiz_results, если они еще не существуют
# quiz_state - таблица, в который хранится user_id пользователя и question_index(вопрос, на котором остановился пользователь)
# quiz_results - таблица, в который хранится user_id пользователя и correct_answers(количество правильных ответов пользователя)
async def create_table():
    # Создаем соединение с базой данных (если она не существует, то она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Выполняем SQL-запрос к базе данных
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_results (user_id INTEGER PRIMARY KEY, correct_answers INTEGER)''')
        # Сохраняем изменения
        await db.commit()

# Функция для обновления количества правильных ответов для конкретного пользователя в таблице quiz_results
async def update_quiz_results(user_id, correct_answers):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_results (user_id, correct_answers) VALUES (?, ?)', (user_id, correct_answers))
        await db.commit()

# Функции для получения количества правильных ответов для конкретного пользователя
async def get_quiz_results(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT correct_answers FROM quiz_results WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


# Функция для обновления индекса текущего вопроса для пользователя в таблице quiz_state
async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        # Сохраняем изменения
        await db.commit()


# Функция получения текущего значения question_index в базе данных для заданного пользователя
async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0
