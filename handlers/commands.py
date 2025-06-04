from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.menu_services import handle_start_command, show_language_selection, show_profile, show_goal_selection, show_about, show_send_image, show_user_sex_selection, show_params_selection, show_daily_kcal, show_nutrition_plan

start_cmd_router = Router()

@start_cmd_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    await handle_start_command(user_id, message, state, bot)

@start_cmd_router.message(Command('lang'))
async def cmd_lang(message: Message):
    await show_language_selection(message)
    await message.delete()

@start_cmd_router.message(Command('profile'))
async def cmd_profile(message: Message):
    user_id = message.from_user.id
    await show_profile(user_id, message)
    await message.delete()

@start_cmd_router.message(Command('goal'))
async def cmd_goal(message: Message):
    user_id = message.from_user.id
    await show_goal_selection(user_id, message)
    await message.delete()

@start_cmd_router.message(Command('about'))
async def cmd_about(message: Message):
    user_id = message.from_user.id
    await show_about(user_id, message)
    await message.delete()

@start_cmd_router.message(Command('recognize'))
async def cmd_image(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await show_send_image(user_id, message, state)
    await message.delete()

@start_cmd_router.message(Command('change_sex'))
async def cmd_sex(message: Message):
    user_id = message.from_user.id
    await show_user_sex_selection(user_id, message)
    await message.delete()

@start_cmd_router.message(Command('change_params'))
async def cmd_params(message: Message):
    user_id = message.from_user.id
    await show_params_selection(user_id, message)
    await message.delete()

@start_cmd_router.message(Command('daily_calories'))
async def cmd_daily_kcal(message: Message):
    user_id = message.from_user.id
    await show_daily_kcal(user_id, message)
    await message.delete()

@start_cmd_router.message(Command('nutrition_plan'))
async def cmd_nutrition_plan(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await show_nutrition_plan(user_id, message, state)
    await message.delete()

