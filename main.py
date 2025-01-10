import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config import API_TOKEN
from database import update_quiz_index, get_quiz_index, create_table, update_quiz_results, get_quiz_results
from quiz import new_quiz, get_question
from quiz_data import quiz_data


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start. При вводе команды /start бот отправляет сообщение с кнопкой "Начать игру". При нажатии на кнопку, пользователь запускает квиз
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем сборщика клавиатур типа Reply
    builder = ReplyKeyboardBuilder()
    # Добавляем в сборщик одну кнопку
    builder.add(types.KeyboardButton(text="Начать игру"))
    # Прикрепляем кнопки к сообщению
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /quiz. Эта команда тоже запускает квиз, вызывая функцию new_quiz (в файле quiz.py)
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    # Отправляем новое сообщение без кнопок
    await message.answer(f"Давайте начнем квиз!")
    # Запускаем новый квиз
    await new_quiz(message)


# Хэндлер на команду /stats. Отображает количество правильных ответов, которые пользователь дал в предыдущем квизе
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    correct_answers = await get_quiz_results(message.from_user.id)
    await message.answer(f"Ваш последний результат: {correct_answers} правильных ответов.")


## Функция для перехватчика колбэк запросов "right_answer" и "wrong_answer"
'''
При нажатии на одну из кнопок с вариантами ответа, происходит обработка колбэк-запросов
Если ответ правильный, увеличивается счетчик правильных ответов
После каждого ответа обновляется индекс текущего вопроса
'''
async def handle_answer(callback: types.CallbackQuery, is_correct: bool):
    # Редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса для данного пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    # Сообщение в зависимости от правильности ответа
    if is_correct:
        await callback.message.answer(
            f"Верно! Вы выбрали: {quiz_data[current_question_index]['options'][correct_option]}")
    else:
        await callback.message.answer(
            f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    # Увеличиваем количество правильных ответов, если ответ был правильный
    if is_correct:
        correct_answers = await get_quiz_results(callback.from_user.id)
        correct_answers += 1
        await update_quiz_results(callback.from_user.id, correct_answers)

    # Проверяем достигнут ли конец квиза
    if current_question_index < len(quiz_data):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


# Функция колбек запроса для right_answer
@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await handle_answer(callback, is_correct=True)


# Функция колбек запроса для wrong_answer
@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await handle_answer(callback, is_correct=False)


async def main():
    # Запускаем создание таблицы базы данных
    await create_table()
    # Запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
