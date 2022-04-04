import aiogram

from src.bot import dp
from config import logger

if __name__ == '__main__':
    logger.error("START USER BOT")
    aiogram.executor.start_polling(dp, skip_updates=True)