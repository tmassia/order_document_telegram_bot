import os
import logging
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

downloads_directory = '/mnt/e/Tatiana/PROJs/TELEGRAMM/document_send_bot/downloads'


# Основная команда /start
@dp.message(F.text == '/start')
async def cmd_start(message: Message):
    await message.answer('ברוכים הבאים לאייקון מעבדות נא לעלות מסמך!')


# Получение id/имени с помощью message.from_user.id
@dp.message(F.text == '/my_id')
async def cmd_my_id(message: Message):
    await message.answer(f'Ваш ID: {message.from_user.id}')
    await message.reply(f'Ваше имя: {message.from_user.first_name}')


@dp.message(F.document)
async def get_document(message: Message):
    # Получите информацию о файле
    file_info = await bot.get_file(message.document.file_id)
    file_path_on_telegram = file_info.file_path

    # Определите имя файла
    file_name = os.path.basename(file_path_on_telegram)

    # Полный путь для сохранения файла на вашем сервере
    destination_path = os.path.join(downloads_directory, file_name)

    # Скачайте и сохраните файл
    await bot.download_file(file_path_on_telegram, destination_path)

    # Отправьте ответное сообщение с идентификатором файла
    await message.answer(
        f"Файл с идентификатором {message.document.file_id} успешно скачан и сохранен как {destination_path}")


# Хэндлер без фильтра, сработает, если ни один выше не сработает.
@dp.message()
async def echo(message: Message):
    await message.answer('Я тебя не понимаю...')


# Polling, т.е бесконечный цикл проверки апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
