import os
import logging
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from send_email import send_email_with_attachment

load_dotenv()

email_to = os.getenv('SMTP_reciever')
subject = "Here is your document"
body = "Please find the attached document."
app_password = os.getenv('SMTP_APP_PASSWORD')
sender_email = os.getenv('SMTP_sender')

# DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

downloads_directory = os.getenv('directory')


# Основная команда /start
@dp.message(F.text == '/start')
async def cmd_start(message: Message):
    await message.answer('Hello in Doc_send_bot!You can send me your document and I will send it to you')


# Получение id/имени с помощью message.from_user.id
@dp.message(F.text == '/my_id')
async def cmd_my_id(message: Message):
    await message.answer(f'Your ID: {message.from_user.id}')
    await message.reply(f'Your name: {message.from_user.first_name}')


@dp.message(F.document)
async def get_document(message: Message):
    # Get info about file
    file_info = await bot.get_file(message.document.file_id, request_timeout=60)
    file_path_on_telegram = file_info.file_path

    # name of file
    file_name = os.path.basename(file_path_on_telegram)

    # full path to file and name
    destination_path = os.path.join(downloads_directory, file_name)

    # Download file and save it
    await bot.download_file(file_path_on_telegram, destination_path)
    try:
        await send_email_with_attachment(email_to, subject, body, destination_path, app_password, sender_email)
        # send message answer with file id
        await message.answer(
            f"File with id {message.document.file_id} successful downloaded and saved as  {destination_path}")
    except Exception as e:
        logger.error(f"An error occurred while processing the document: {str(e)}")
        await message.answer(f"An error occurred while sending the document: {str(e)}")


# handler for any other message
@dp.message()
async def echo(message: Message):
    await message.answer('I dont understand you..')


# Polling, updates cycle
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
