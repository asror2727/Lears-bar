import asyncio
import logging

from bot_instance import bot, dp
from database import init_db
from handlers import admin, common, game_play, registration, shop


async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()

    dp.include_router(common.router)
    dp.include_router(registration.router)
    dp.include_router(game_play.router)
    dp.include_router(shop.router)
    dp.include_router(admin.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
