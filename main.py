import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

from config import BOT_TOKEN
import config
from database import Database
from handlers import user_handlers, admin_handlers
from keyboards import get_support_buttons

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class BanCheckMiddleware(BaseMiddleware):
    """Cheklangan foydalanuvchilarni bloklash middleware"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Admin uchun tekshirmaslik
        user_id = event.from_user.id
        if user_id == config.ADMIN_ID:
            return await handler(event, data)
        
        # /start buyrug'ini o'tkazib yuborish (u o'zida tekshiradi)
        if isinstance(event, Message) and event.text and event.text.startswith('/start'):
            return await handler(event, data)
        
        # Foydalanuvchi cheklangan yoki yo'qligini tekshirish
        if self.db.is_user_banned(user_id):
            if isinstance(event, Message):
                await event.answer(
                    "🚫 **Sizning botdan foydalanish huquqingiz yo'q.**\n\n"
                    "Agar bu xato deb hisoblasangiz yoki huquqni qaytadan olish uchun "
                    "qo'llab-quvvatlash guruhiga murojaat qiling:",
                    reply_markup=get_support_buttons(config.SUPPORT_GROUP_URL),
                    parse_mode="Markdown"
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "🚫 Sizning botdan foydalanish huquqingiz yo'q.",
                    show_alert=True
                )
            return
        
        # Foydalanuvchi cheklanmagan - davom etish
        return await handler(event, data)

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
    
    # Middleware qo'shish - barcha user handlerlar uchun
    user_handlers.router.message.middleware(BanCheckMiddleware())
    user_handlers.router.callback_query.middleware(BanCheckMiddleware())
    
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    
    logger.info("Bot ishga tushdi!")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
