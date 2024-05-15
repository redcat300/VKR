import aiogram
import asyncio
import logging
import openai

from token_data import TOKEN
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from token_data import TOKEN
from API_data import openai_api_key
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from Data_questions import faq

openai.api_key = openai_api_key

bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

messages = []

async def start_chat_gpt(request, messages):
    try:
        messages.append({'role': 'user', 'content': request})

        chat = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages
        )

        answer = chat.choices[0].message.content
        messages.append({'role': 'assistant', 'content': answer})
    except Exception as e:
        logging.error(f'Error: {e}')
        answer = "Произошла ошибка при обработке запроса."

    return answer

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
       kb = [
          [
              types.KeyboardButton(text="FAQ"),
          ],
       ]
       keyboard = types.ReplyKeyboardMarkup(
           keyboard=kb,
           resize_keyboard=True,
       )
       username = message.chat.username
       await message.answer(f'Привет {username}! Я бот с искусственным интеллектом. Задайте мне свой вопрос, и я постараюсь на него ответить.', reply_markup=keyboard)

@dp.message()
async def chat_handler_FAQ(message: Message):
    try:
        if message.text.lower() == "faq":
            await message.answer (
                "Вот список часто задаваемых вопросов:\n"
                "1. Какие услуги предоставляет ваша IT-компания?\n"
                "2. Сколько времени займет разработка моего проекта?\n"
                "3. Каковы ваши цены на услуги?\n"
                "4. Как вы обеспечиваете безопасность данных?\n"
                "5. Предоставляете ли вы поддержку после запуска проекта?\n"
                "6. Какой у вас опыт работы в нашей отрасли?\n"
                "7. Каков процесс разработки проекта в вашей компании?\n"
                "8. Какие языки программирования и технологии вы используете?\n"
                "9. Как вы справляетесь с изменениями в проекте в процессе его разработки?\n"
                "10. Каковы условия оплаты за ваши услуги?\n"
            )
        else:
            loading_info = await message.answer('Думаю...')
            text_answer = await start_chat_gpt(message.text, messages)
            await message.answer(text_answer, parse_mode=ParseMode.MARKDOWN)
            await bot.delete_message(message.chat.id, loading_info.message_id)
    except Exception as e:
        logging.error(f'Error: {e}')

@dp.callback_query(lambda c: c.data.startswith('faq_'))
async def process_faq(callback_query: types.CallbackQuery):
    try:
        question = callback_query.data.split('_')[1]
        await bot.send_message(callback_query.from_user.id, faq[question])
        await callback_query.answer()
    except Exception as e:
        logging.error(f'Error: {e}')

@dp.message()
async def chat_handler(message: Message):
    try:
        loading_info = await message.answer('Думаю...')
        text_answer = await start_chat_gpt(message.text, messages)
        await message.answer(text_answer, parse_mode=ParseMode.MARKDOWN)
        await bot.delete_message(message.chat.id, loading_info.message_id)
    except Exception as e:
        logging.error(f'Error: {e}')

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
