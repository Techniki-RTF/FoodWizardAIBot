from aiogram import Router, F, Bot
from aiogram.exceptions import *
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import UserStates
from keyboards.inline_keyboard import *
from db_handler.database import *
from utils.converters import *
from utils.msj_equation import msj_equation
from utils.gemini import generate_nutrition_plan

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
    c_profile = (await get_profile(callback.from_user.id))
    c_profile = {k: 'нет данных' if v in ('', None) else v for k, v in c_profile.items()}
    await callback.message.edit_text(
        f"Ваша цель: {goal_converter(c_profile['goal'])}\n"
        f"Ваш пол: {user_sex_converter(c_profile['sex'])}\n"
        f"Ваши текущие параметры: {c_profile['height']} см / {c_profile['weight']} кг / {c_profile['age']} лет\n"
        f"Ваш индекс массы тела: {bmi_converter(c_profile['bmi']) if type(c_profile['bmi']) in {float, int}  else 'нет данных'}\n"
        f"Ваша дневная норма калорий с учётом вашей активности ({activity_converter(c_profile['activity'])}): {c_profile['daily_kcal']}",
        reply_markup=profile_kb())

@start_cmd_router.callback_query(F.data == 'goal')
async def goal(callback: CallbackQuery):
    c_profile = (await get_profile(callback.from_user.id))
    await callback.message.edit_text(
        f"Выберете цель:{bmi_to_goal_converter(c_profile['bmi'])}",
        reply_markup=goal_kb(c_profile['bmi']))

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

@start_cmd_router.callback_query(F.data.in_({'lose_weight', 'maintain_weight', 'mass_gain'}))
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

@start_cmd_router.callback_query(F.data == 'daily_kcal')
async def daily_kcal(callback: CallbackQuery):
    c_profile = (await get_profile(callback.from_user.id))
    await callback.message.edit_text('Выберете ваш уровень активности:', reply_markup=daily_kcal_kb(c_profile['activity']))

@start_cmd_router.callback_query(F.data.regexp(r'activity_[0-4]$'))
async def daily_kcal_activity(callback: CallbackQuery):
    user_id = callback.from_user.id
    c_profile = await get_profile(user_id)
    await change_activity(user_id, int(callback.data[-1]))
    msj = msj_equation(c_profile, callback.data[-1])
    await change_daily_kcal(user_id, msj[1])
    await callback.message.edit_text(f'{msj[0]}', reply_markup=back_home_kb())

@start_cmd_router.callback_query(F.data == 'nutrition_plan')
async def nutrition_plan(callback: CallbackQuery, bot: Bot):
    c_profile = (await get_profile(callback.from_user.id))
    c_daily_kcal = c_profile['daily_kcal']
    if not c_daily_kcal:
        await callback.message.edit_text(text=f"Заполните профиль и рассчитайте вашу суточную норму калорий перед использованием этой функции", reply_markup=back_home_kb())
        return
    await callback.message.edit_text(text=f"План питания на {c_profile['daily_kcal']} ккал в день создаётся...")
    await bot.send_chat_action(callback.message.chat.id, 'typing')
    response = await generate_nutrition_plan(c_profile['daily_kcal'], goal_converter(c_profile['goal']))
    match response:
        case 'api_error':
            await callback.message.edit_text('Произошла непредвиденная ошибка, попробуйте ещё раз', reply_markup=back_home_kb())
        case _:
            days = response.get('days', [])
            if not days:
                await callback.message.edit_text('Не удалось составить план питания, попробуйте ещё раз', reply_markup=back_home_kb())
                return
                
            full_plan = f"🍽️ План питания на неделю ({c_profile['daily_kcal']} ккал/день)\n\n"
            
            for day in days:
                day_name = day['day_name'].capitalize()
                day_calories = day['calories']
                day_proteins = day['proteins']
                day_fats = day['fats']
                day_carbs = day['carbs']
                
                full_plan += f"📅 {day_name} (Б: {day_proteins}г, Ж: {day_fats}г, У: {day_carbs}г, {day_calories} ккал)\n\n"
                
                breakfast = day['breakfast'][0]
                full_plan += f"🍳 Завтрак: {breakfast['dish_name']}\n"
                full_plan += f"{breakfast['description']}\n"
                full_plan += f"Б: {breakfast['proteins']}г, Ж: {breakfast['fats']}г, У: {breakfast['carbs']}г, {breakfast['calories']} ккал\n\n"
                
                lunch = day['lunch'][0]
                full_plan += f"🥗 Обед: {lunch['dish_name']}\n"
                full_plan += f"{lunch['description']}\n"
                full_plan += f"Б: {lunch['proteins']}г, Ж: {lunch['fats']}г, У: {lunch['carbs']}г, {lunch['calories']} ккал\n\n"
                
                dinner = day['dinner'][0]
                full_plan += f"🍲 Ужин: {dinner['dish_name']}\n"
                full_plan += f"{dinner['description']}\n"
                full_plan += f"Б: {dinner['proteins']}г, Ж: {dinner['fats']}г, У: {dinner['carbs']}г, {dinner['calories']} ккал\n\n"
                
                full_plan += "➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            await callback.message.delete()
            await callback.message.answer(full_plan, reply_markup=plan_response_kb())
