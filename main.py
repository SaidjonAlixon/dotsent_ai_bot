import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import Database
from handlers import user_handlers, admin_handlers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Bot ishga tushirish"""
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN topilmadi! .env faylini to'ldiring.")
        return
    
    logger.info("Bot ishga tushmoqda...")
    
    db = Database()
    logger.info("Ma'lumotlar bazasi tayyor")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    
    logger.info("Bot ishga tushdi!")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
