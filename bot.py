import logging
import os
import aiohttp
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType, ChatActions


# bot token
TG_TOKEN = os.getenv("TG_TOKEN")

# webhook settings
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f'/webhook/{TG_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("PORT"))

# qa api host
API_HOST = os.getenv("API_HOST")


# Initialize bot and dispatcher
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


async def on_startup(dispatcher: Dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher: Dispatcher):
    logging.warning('Shutting down ...')
    await bot.delete_webhook()
    logging.warning('Bye!')


# TODO add more complex error handling
async def get_answer(question: str):
    if question and question.strip():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_HOST}/api/ask", params={"question": question}) as response:
                    qa_data = await response.json()
                    if response.ok:
                        return qa_data[0]['qa_doc']['answer']
                    else:
                        return "Вибачте, щось пішло не так. Спробуйте, будь ласка, пізніше."
        except Exception as e:
            logging.error(str(e))
            return 'Щось пішло не так, спробуйте, будь ласка, пізніше'


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привіт! З радістю відповім на всі ваші питання щодо університету")


@dp.message_handler(commands=['about'])
async def send_about(msg: types.Message):
    await msg.answer("🤖 Даний бот відповість на ваші питання щодо універу, відправьте питання, щоб отримати відповідь")


# TODO make return mark up message with button more
@dp.message_handler(content_types=ContentType.TEXT)
async def text_handler(message: types.Message):
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    answer = await get_answer(message.text)
    await message.answer(answer)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )
