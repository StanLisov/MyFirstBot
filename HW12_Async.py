import HW12_Async_DATA
import HW12_Async2
import nest_asyncio
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)
API_TOKEN = '6810339571:AAFZtqmFCkRAiVQcEZerv5QCD0uekaw7d-o'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def generate_options_keyboard(answer_options, right_answer):
  builder = InlineKeyboardBuilder()
  for option in answer_options:
      builder.add(types.InlineKeyboardButton(text=option, callback_data="right_answer" if option == right_answer else "wrong_answer"))
  builder.adjust(1)
  return builder.as_markup()

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
  await callback.bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=None)
  await callback.message.answer("Верно!")
  current_question_index = await HW12_Async2.get_quiz_index(callback.from_user.id)
  current_question_index += 1
  score = await HW12_Async2.get_score(callback.from_user.id)
  score += 1
  await HW12_Async2.update_quiz_index(callback.from_user.id, current_question_index, score)
  if current_question_index < len(HW12_Async_DATA.quiz_data):
    await get_question(callback.message, callback.from_user.id)
  else:
    await callback.message.answer("Это был последний вопрос. Квиз завершен!")
    old_score = score
    score = score * 10
    await callback.message.answer(f"Ваш результат: {old_score}/10 ({score}%)")

@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
  await callback.bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=None)
  current_question_index = await HW12_Async2.get_quiz_index(callback.from_user.id)
  correct_option = HW12_Async_DATA.quiz_data[current_question_index]['correct_option']
  await callback.message.answer(f"Неправильно. Правильный ответ: {HW12_Async_DATA.quiz_data[current_question_index]['options'][correct_option]}")
  current_question_index += 1
  score = await HW12_Async2.get_score(callback.from_user.id)
  await HW12_Async2.update_quiz_index(callback.from_user.id, current_question_index, score)
  if current_question_index < len(HW12_Async_DATA.quiz_data):
    await get_question(callback.message, callback.from_user.id)
  else:
    await callback.message.answer("Это был последний вопрос. Квиз завершен!")
    old_score = score
    score = score * 10
    await callback.message.answer(f"Ваш результат: {old_score}/10 ({score}%)")

async def get_question(message, user_id):
  current_question_index = await HW12_Async2.get_quiz_index(user_id)
  correct_index = HW12_Async_DATA.quiz_data[current_question_index]['correct_option']
  opts = HW12_Async_DATA.quiz_data[current_question_index]['options']
  kb = generate_options_keyboard(opts, opts[correct_index])
  await message.answer(f"{HW12_Async_DATA.quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
  user_id = message.from_user.id
  current_question_index = 0
  score = 0
  await HW12_Async2.update_quiz_index(user_id, current_question_index, score)
  await get_question(message, user_id)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
  builder = ReplyKeyboardBuilder()
  builder.add(types.KeyboardButton(text="Начать игру"))
  await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
  await message.answer(f"Давайте начнем квиз!")
  await new_quiz(message)

@dp.message(Command("result"))
async def result(message: types.Message):
  user_id = message.from_user.id
  score = await HW12_Async2.get_score(user_id)
  old_score = score
  score = score * 10
  await message.answer(f"Ваш последний результат: {old_score}/10 ({score}%)")

async def main():
  await HW12_Async2.create_table()
  await dp.start_polling(bot)
if __name__ == "__main__":
  asyncio.run(main())

