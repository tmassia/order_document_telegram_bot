import os
import logging
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

# #from proj
from handlers.start_handlers import start_router
from handlers.bdika_gilui_handlers import bdika_gilui_router

# Load environment variables from a .env file
load_dotenv()
# Get the bot token from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
# Initialize the bot
bot = Bot(token=BOT_TOKEN)
# Initialize the dispatcher
dp = Dispatcher()


# Register handlers from other modules
# Polling, updates cycle

# Define a function to start the polling and handle updates
# Register handlers from other modules
# Polling, updates cycle
async def main():
    # Register handlers
    dp.include_router(start_router)
    dp.include_router(bdika_gilui_router)
    # Start polling for updates
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


# Define an echo function to respond when a message is not understood
async def echo(message: Message):
    await message.answer('I dont understand you..')


# Entry point of the script
if __name__ == '__main__':
    try:
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        # Run the main function to start the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
