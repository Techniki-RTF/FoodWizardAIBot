import asyncio
from create_bot import bot, dp, logger
from handlers.commands import start_cmd_router
from handlers.messages import start_msg_router

async def main():
    dp.include_router(start_cmd_router)
    dp.include_router(start_msg_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Бот остановлен')
