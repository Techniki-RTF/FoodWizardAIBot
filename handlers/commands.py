from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import UserStates
from keyboards.inline_keyboard import *
from utils.converters import *

start_cmd_router = Router()

@start_cmd_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет! Меню:', reply_markup=main_menu_kb())

@start_cmd_router.callback_query(F.data == 'back_home')
async def back_home(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await callback.answer('На главную')
    await callback.message.edit_text('Привет! Меню:', reply_markup=main_menu_kb())

@start_cmd_router.callback_query(F.data == 'send_image')
async def send_image(callback: CallbackQuery, state: FSMContext):
    await state.update_data(original_message_id=callback.message.message_id)
    await state.set_state(UserStates.waiting_for_image)
    await callback.message.edit_text('Отправьте изображение', reply_markup=back_home_kb())

@start_cmd_router.callback_query(F.data == 'about')
async def about(callback: CallbackQuery):
    await callback.message.edit_text(
        "Разработчик: t.me/renamq\n"
             "Команда: Техники",
             reply_markup=back_home_kb())

@start_cmd_router.callback_query(F.data == 'profile')
async def profile(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Ваша цель: {None}\n"
        f"Ваши текущие параметры: {None} см / {None} кг / {None} лет\n",
        reply_markup=profile_kb())

@start_cmd_router.callback_query(F.data == 'goal')
async def goal(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Выберете цель:",
        reply_markup=goal_kb())

@start_cmd_router.callback_query(F.data == 'params')
async def params(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Выберете параметр для изменения его значения",
        reply_markup=params_kb())

@start_cmd_router.callback_query(F.data.in_({'lose_weight', 'maintain_weight', 'gain_mass'}))
async def c_goal(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Вы выбрали {goal_converter(callback.data)} в качестве цели",
        reply_markup=back_home_kb())

@start_cmd_router.callback_query(F.data.in_({'c_height', 'c_weight', 'c_age'}))
async def c_param(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Отправьте значение параметра в формате {params_converter(callback.data)}",
        reply_markup=back_home_kb()
    )