from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db_handler.database import create_user, get_user_lang
from handlers.callbacks import lang
from utils.delete_menu_message import delete_menu_message
from utils.locales import get_user_translator

start_cmd_router = Router()

@start_cmd_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await delete_menu_message(message, state, bot)
    await message.delete()
    user_id = message.from_user.id
    await create_user(user_id)
    if not await get_user_lang(user_id):
        await lang(message=message)
        return
    _ = await get_user_translator(user_id)
    answer = await message.answer(_("Hello, {name}!\nMenu:").format(name=message.from_user.full_name), reply_markup=await main_menu_kb(user_id=user_id))
    await state.update_data(menu_message_id=answer.message_id)