from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db_handler.database import *
from keyboards.inline_keyboard import *
from states import UserStates
from utils.converters import *
from utils.gemini import generate_recipe
from utils.image_data import get_image_data
from utils.msj_equation import msj_equation

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
        reply_markup=back_kb('profile'))

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
        reply_markup=back_kb('profile'))

@start_cmd_router.callback_query(F.data.in_({'c_height', 'c_weight', 'c_age'}))
async def c_param(callback: CallbackQuery, state: FSMContext):
    await state.update_data(original_message_id=callback.message.message_id)
    await state.set_state(UserStates.waiting_for_param)
    await state.update_data(param=callback.data)
    await callback.message.edit_text(
        f"Отправьте значение параметра в формате {params_converter(callback.data)}",
        reply_markup=back_kb('params')
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
async def nutrition_plan(callback: CallbackQuery, state: FSMContext):
    c_profile = (await get_profile(callback.from_user.id))
    c_daily_kcal = c_profile['daily_kcal']
    if not c_daily_kcal:
        await callback.message.edit_text(text=f"Заполните профиль и рассчитайте вашу суточную норму калорий перед использованием этой функции",
                                         reply_markup=back_home_kb())
        return
    await state.set_state(UserStates.waiting_for_diet_preferences)
    await state.update_data(original_message_id=callback.message.message_id)
    await callback.message.edit_text(text="Укажите особые предпочтения в вашем рационе, если они есть\n"
                                          "Примеры: десерты в приёмах пищи, вегетарианская диета, непереносимость цитрусовых\n"
                                          "Если у вас нет особых предпочтений, напишите \"Нет\"", reply_markup=back_home_kb())

@start_cmd_router.callback_query(F.data == 'find_recipe')
async def recipe_choose(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    file_bytes, input_file = await get_image_data(callback.message, bot)

    dishes = [line.replace('Название блюда:', '').strip() for line in callback.message.caption.split('\n')
              if line.startswith('Название блюда:')]
    
    await state.set_state(UserStates.waiting_for_recipe)
    await state.update_data(file_bytes=file_bytes)

    answer = await callback.message.answer_photo(
        photo=input_file, 
        caption='Для какого блюда найти рецепт?', 
        reply_markup=recipe_list_kb(dishes)
    )
    
    await state.update_data(original_message_id=answer.message_id)

@start_cmd_router.callback_query(F.data.regexp(r'recipe_..*'))
async def recipe_find(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    file_bytes = state_data.get('file_bytes')

    dish = callback.data.replace('recipe_', '')

    await callback.message.edit_caption(caption='Поиск рецепта в процессе', reply_markup=None)
    response = await generate_recipe(dish, file_bytes)
    
    await state.clear()
    
    match response:
        case 'api_error':
            await callback.message.edit_caption(
                caption='Произошла непредвиденная ошибка, попробуйте ещё раз',
                reply_markup=back_home_kb()
            )
        case _:
            recipes = response.get('recipes', [])
            if not recipes:
                await callback.message.edit_caption(
                    caption='Не удалось найти рецепт, попробуйте ещё раз',
                    reply_markup=back_home_kb()
                )
                return

            recipe = recipes[0]

            full_recipe = f"🍽️ {recipe['dish_name']}\n\n"

            full_recipe += f"📊 Пищевая ценность (на 100г):\n"
            full_recipe += f"🔸 Калории: {recipe['nutritional_info']['calories']} ккал\n"
            full_recipe += f"🔸 Белки: {recipe['nutritional_info']['protein']}г\n"
            full_recipe += f"🔸 Жиры: {recipe['nutritional_info']['fats']}г\n"
            full_recipe += f"🔸 Углеводы: {recipe['nutritional_info']['carbs']}г\n\n"

            full_recipe += "📝 Ингредиенты:\n"
            for i, ingredient in enumerate(recipe['ingredients'], 1):
                full_recipe += f"{i}. {ingredient}\n"
            full_recipe += "\n"

            full_recipe += "👨‍🍳 Способ приготовления:\n"
            for i, step in enumerate(recipe['recipe'], 1):
                full_recipe += f"{i}. {step}\n"

            try:
                await callback.message.edit_caption(caption=full_recipe, reply_markup=home_kb())
            except TelegramBadRequest:
                header = f"🍽️ {recipe['dish_name']}\n\n"
                header += f"📊 Пищевая ценность (на 100г):\n"
                header += f"🔸 Калории: {recipe['nutritional_info']['calories']} ккал\n"
                header += f"🔸 Белки: {recipe['nutritional_info']['protein']}г\n"
                header += f"🔸 Жиры: {recipe['nutritional_info']['fats']}г\n"
                header += f"🔸 Углеводы: {recipe['nutritional_info']['carbs']}г\n"
                
                ingredients = "📝 Ингредиенты:\n"
                for i, ingredient in enumerate(recipe['ingredients'], 1):
                    if ingredient not in ['recipe', 'nutritional_info']:
                        ingredients += f"{i}. {ingredient}\n"
                
                cooking = "👨‍🍳 Способ приготовления:\n"
                for i, step in enumerate(recipe['recipe'], 1):
                    cooking += f"{i}. {step}\n"
                
                await callback.message.edit_caption(caption=header, reply_markup=None)
                await callback.message.answer(ingredients)
                await callback.message.answer(cooking, reply_markup=home_kb())

@start_cmd_router.callback_query(F.data == 'find_food_swap')
async def find_food_swap(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    file_bytes, input_file = await get_image_data(callback.message, bot)

    await state.set_state(UserStates.waiting_for_food_swap)
    await state.update_data(file_bytes=file_bytes)
    
    answer = await callback.message.answer_photo(
        caption="Укажите, какие ингредиенты вы хотели бы заменить на более низкокалорийные альтернативы.\n"
                "Например: \"заменить масло, сметану и сахар\" или \"все ингредиенты\"",
        photo=input_file,
        reply_markup=cancel_kb()
    )
    
    await state.update_data(original_message_id=answer.message_id)

@start_cmd_router.callback_query(F.data == 'cancel')
async def cancel_recipe(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    match current_state:
        case UserStates.waiting_for_recipe:
            await state.clear()
            await callback.answer('Поиск рецепта отменен')
            await callback.message.delete()
        case UserStates.waiting_for_food_swap:
            await state.clear()
            await callback.answer('Поиск альтернатив отменен')
            await callback.message.delete()
        case _:
            await callback.answer()
            await callback.message.delete()
