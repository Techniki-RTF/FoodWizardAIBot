import asyncio
from create_bot import bot, dp, logger
from handlers.callbacks import start_callback_router
from handlers.messages import start_msg_router
from handlers.commands import start_cmd_router
from db_handler import database
from utils.locales import LanguageSelectionRequired
from aiogram.types import ErrorEvent
from aiogram import F


async def main():
    await database.init_db()
    dp.include_router(start_callback_router)
    dp.include_router(start_msg_router)
    dp.include_router(start_cmd_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


@dp.errors()
async def error_handler(error_event: ErrorEvent):
    if isinstance(error_event.exception, LanguageSelectionRequired):
        # Просто игнорируем это исключение, так как меню выбора языка уже показано
        return True
    logger.error(f"Необработанное исключение: {error_event.exception}")
    return None


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Бот остановлен')
