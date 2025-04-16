from bot.config import settings

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger
from bot.database.create_db import create_tables
from bot.handlers.registration import register_handlers, router
from bot.utils import check_payment_deadline, check_payment_payed


logger.info("Imported all modules. Starting bot...")

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    dp.include_router(router)
    logger.info("Handler registration starts")
    register_handlers()
    logger.info("Handlers registered")
    
    await create_tables()
    
    asyncio.create_task(check_payment_payed(bot))
    asyncio.create_task(check_payment_deadline(bot))
    
    
    await bot(DeleteWebhook(drop_pending_updates=True))
    bot_info = await bot.get_me()
    
    logger.info(f"bot ID: {bot_info.id}")
    logger.info(f"bot username: {bot_info.username}")
    logger.info(f"bot link: https://t.me/{bot_info.username}")
    logger.info("Bot started")
    await dp.start_polling(bot)

    
if __name__ == '__main__':
    asyncio.run(main())
