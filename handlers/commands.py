from aiogram import Router, F, Bot
from aiogram.exceptions import *
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import UserStates
from keyboards.inline_keyboard import *
from db_handler.database import *

start_cmd_router = Router()

async def delete_menu_message(message, current_state, bot):
    data = await current_state.get_data()
    menu_message_id = data.get('menu_message_id')
    if menu_message_id:
        try:
            await bot.delete_message(message.chat.id, menu_message_id)
        except TelegramBadRequest:
            pass

@start_cmd_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await delete_menu_message(message, state, bot)
    await message.delete()
    await create_user(message.from_user.id)
    answer = await message.answer(f'Привет, {message.from_user.full_name}!\nМеню:', reply_markup=main_menu_kb())
    await state.update_data(menu_message_id=answer.message_id)

@start_cmd_router.callback_query(F.data == 'home')
async def home(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await delete_menu_message(callback.message, state, bot)
    await callback.answer()
    answer = await callback.message.answer(f'Привет, {callback.from_user.full_name}!\nМеню:', reply_markup=main_menu_kb())
    await state.update_data(menu_message_id=answer.message_id)


@start_cmd_router.callback_query(F.data == 'back_home')
async def back_home(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await callback.message.edit_text(f'Привет, {callback.from_user.full_name}!\nМеню:', reply_markup=main_menu_kb())

@start_cmd_router.callback_query(F.data == 'send_image')
async def send_image(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(UserStates.waiting_for_image)
    if callback.message.photo:
        answer = await callback.message.answer(text='Отправьте изображение', reply_markup=back_home_kb())
        await state.update_data(original_message_id=answer.message_id)
    else:
        await state.update_data(original_message_id=callback.message.message_id)
        await callback.message.edit_text('Отправьте изображение', reply_markup=back_home_kb())

@start_cmd_router.callback_query(F.data == 'about')
async def about(callback: CallbackQuery):
    await callback.message.edit_text(
        "Разработчик: t.me/renamq\n"
             "Команда: Техники",
             reply_markup=back_home_kb())

@start_cmd_router.callback_query(F.data == 'profile')
async def profile(callback: CallbackQuery):
    c_profile = await get_profile(callback.from_user.id)
    await callback.message.edit_text(
        f"Ваша цель: {c_profile['goal']}\n"
        f"Ваш пол: {c_profile['sex']}\n"
        f"Ваши текущие параметры: {c_profile['height']} см / {c_profile['weight']} кг / {c_profile['age']} лет\n",
        reply_markup=profile_kb())

@start_cmd_router.callback_query(F.data == 'goal')
async def goal(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Выберете цель:",
        reply_markup=goal_kb())

@start_cmd_router.callback_query(F.data == 'sex')
async def goal(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Выберете пол:",
        reply_markup=user_sex_kb())

@start_cmd_router.callback_query(F.data.in_({'male', 'female'}))
async def c_goal(callback: CallbackQuery):
    await change_user_sex(callback.from_user.id, callback.data)
    await callback.message.edit_text(
        f"Вы выбрали {user_sex_converter(callback.data)} пол",
        reply_markup=back_home_kb())

@start_cmd_router.callback_query(F.data == 'params')
async def params(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Выберете параметр для изменения его значения",
        reply_markup=params_kb())

@start_cmd_router.callback_query(F.data.in_({'lose_weight', 'maintain_weight', 'gain_mass'}))
async def c_goal(callback: CallbackQuery):
    await change_goal(callback.from_user.id, callback.data)
    await callback.message.edit_text(
        f"Вы выбрали {goal_converter(callback.data)} в качестве цели",
        reply_markup=back_home_kb())

@start_cmd_router.callback_query(F.data.in_({'c_height', 'c_weight', 'c_age'}))
async def c_param(callback: CallbackQuery, state: FSMContext):
    await state.update_data(original_message_id=callback.message.message_id)
    await state.set_state(UserStates.waiting_for_param)
    await state.update_data(param=callback.data)
    await callback.message.edit_text(
        f"Отправьте значение параметра в формате {params_converter(callback.data)}",
        reply_markup=back_params_kb()
    )