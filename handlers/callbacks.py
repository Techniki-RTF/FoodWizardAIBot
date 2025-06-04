from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db_handler.database import *
from keyboards.inline_keyboard import *
from services.menu_services import show_main_menu, show_main_menu_edit, show_profile, show_goal_selection, show_language_selection, show_about, show_send_image, show_user_sex_selection, show_params_selection, show_daily_kcal, show_nutrition_plan
from states import UserStates
from utils.converters import *
from utils.exceptions import GeminiApiError
from utils.gemini import generate_recipe
from utils.image_data import get_image_data
from utils.locales import get_user_translator
from utils.msj_equation import msj_equation

start_callback_router = Router()

@start_callback_router.callback_query(F.data == 'lang')
async def lang(callback: CallbackQuery = None, message: Message = None):
    context = callback if callback else message
    await show_language_selection(context)

@start_callback_router.callback_query(F.data.in_({'ru', 'en'}))
async def lang_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await change_user_lang(callback.from_user.id, callback.data)
    await callback.message.delete()
    await show_main_menu(callback.from_user.id, callback, state, bot)

@start_callback_router.callback_query(F.data == 'home')
async def home(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await show_main_menu(callback.from_user.id, callback, state, bot)

@start_callback_router.callback_query(F.data == 'back_home')
async def back_home(callback: CallbackQuery, state: FSMContext):
    await show_main_menu_edit(callback.from_user.id, callback, state)

@start_callback_router.callback_query(F.data == 'profile')
async def profile(callback: CallbackQuery):
    await show_profile(callback.from_user.id, callback)

@start_callback_router.callback_query(F.data == 'goal')
async def goal(callback: CallbackQuery):
    await show_goal_selection(callback.from_user.id, callback)

@start_callback_router.callback_query(F.data == 'about')
async def about(callback: CallbackQuery):
    await show_about(callback.from_user.id, callback)

@start_callback_router.callback_query(F.data == 'send_image')
async def send_image(callback: CallbackQuery, state: FSMContext):
    await show_send_image(callback.from_user.id, callback, state)

@start_callback_router.callback_query(F.data == 'sex')
async def sex(callback: CallbackQuery):
    await show_user_sex_selection(callback.from_user.id, callback)

@start_callback_router.callback_query(F.data.in_({'male', 'female'}))
async def c_sex(callback: CallbackQuery):
    user_id = callback.from_user.id
    _ = await get_user_translator(user_id, callback)
    await change_user_sex(user_id, callback.data)
    await callback.message.edit_text(
        _("You have selected: {sex}").format(sex=await user_sex_converter(callback.data, user_id)),
        reply_markup=await back_kb('profile', user_id=user_id))

@start_callback_router.callback_query(F.data == 'params')
async def params(callback: CallbackQuery):
    await show_params_selection(callback.from_user.id, callback)

@start_callback_router.callback_query(F.data.in_({'lose_weight', 'maintain_weight', 'mass_gain'}))
async def c_goal(callback: CallbackQuery):
    user_id = callback.from_user.id
    _ = await get_user_translator(user_id, callback)
    await change_goal(user_id, callback.data)
    await callback.message.edit_text(
        _("You have chosen {goal} as your goal").format(goal=await goal_converter(callback.data, user_id)),
        reply_markup=await back_kb('profile', user_id=user_id))

@start_callback_router.callback_query(F.data.in_({'c_height', 'c_weight', 'c_age'}))
async def c_param(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    _ = await get_user_translator(user_id, callback)
    await state.update_data(original_message_id=callback.message.message_id)
    await state.set_state(UserStates.waiting_for_param)
    await state.update_data(param=callback.data)
    await callback.message.edit_text(
        _("Send the parameter value in the format: {param_format}").format(param_format=await params_converter(callback.data, user_id)),
        reply_markup=await back_kb('params', user_id=user_id)
    )

@start_callback_router.callback_query(F.data == 'daily_kcal')
async def daily_kcal(callback: CallbackQuery):
    await show_daily_kcal(callback.from_user.id, callback)

@start_callback_router.callback_query(F.data.regexp(r'activity_[0-4]$'))
async def daily_kcal_activity(callback: CallbackQuery):
    user_id = callback.from_user.id
    c_profile = await get_profile(user_id)
    await change_activity(user_id, int(callback.data[-1]))
    msj = await msj_equation(c_profile, callback.data[-1], user_id)
    await change_daily_kcal(user_id, msj[1])
    await callback.message.edit_text(f'{msj[0]}', reply_markup=await back_home_kb(user_id=user_id))

@start_callback_router.callback_query(F.data == 'nutrition_plan')
async def nutrition_plan(callback: CallbackQuery, state: FSMContext):
    await show_nutrition_plan(callback.from_user.id, callback, state)

@start_callback_router.callback_query(F.data == 'find_recipe')
async def recipe_choose(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback.from_user.id
    _ = await get_user_translator(user_id, callback)
    await callback.answer()
    file_bytes, input_file = await get_image_data(callback.message, bot)

    dishes = [line.replace('Название блюда:', '').strip() for line in callback.message.caption.split('\n')
              if line.startswith('Название блюда:')]
    
    await state.set_state(UserStates.waiting_for_recipe)
    await state.update_data(file_bytes=file_bytes)

    answer = await callback.message.answer_photo(
        photo=input_file, 
        caption=_("Which dish would you like a recipe for?"), 
        reply_markup=await recipe_list_kb(dishes, user_id=user_id)
    )
    
    await state.update_data(original_message_id=answer.message_id)

@start_callback_router.callback_query(F.data.regexp(r'recipe_..*'))
async def recipe_find(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback.from_user.id
    _ = await get_user_translator(user_id, callback)
    await callback.answer()
    dish = callback.data.split('_', 1)[1]
    file_bytes, input_file = await get_image_data(callback.message, bot)

    await callback.message.edit_caption(caption=_("Searching for a recipe..."), reply_markup=None)
    
    try:
        response = await generate_recipe(dish, file_bytes, user_lang=await get_user_lang(user_id))
        
        recipes = response.get('recipes', [])
        if not recipes:
            await callback.message.edit_caption(
                caption=_("Failed to find a recipe. Please try again."),
                reply_markup=await back_home_kb(user_id=user_id)
            )
            return

        recipe = recipes[0]

        full_recipe = f"🍽️ {recipe['dish_name']}\n\n"

        full_recipe += _("📊 Nutritional value (per 100g):") + "\n"
        full_recipe += _("🔸 Calories: {calories} kcal").format(calories=recipe['nutritional_info']['calories']) + "\n"
        full_recipe += _("🔸 Protein: {protein}g").format(protein=recipe['nutritional_info']['protein']) + "\n"
        full_recipe += _("🔸 Fats: {fats}g").format(fats=recipe['nutritional_info']['fats']) + "\n"
        full_recipe += _("🔸 Carbohydrates: {carbs}g").format(carbs=recipe['nutritional_info']['carbs']) + "\n\n"

        full_recipe += _("📝 Ingredients:") + "\n"
        for i, ingredient in enumerate(recipe['ingredients'], 1):
            full_recipe += f"{i}. {ingredient}\n"
        full_recipe += "\n"

        full_recipe += _("👨‍🍳 Preparation method:") + "\n"
        for i, step in enumerate(recipe['recipe'], 1):
            full_recipe += f"{i}. {step}\n"

        try:
            await callback.message.edit_caption(caption=full_recipe, reply_markup=await home_kb(user_id=user_id))
        except TelegramBadRequest:
            header = f"🍽️ {recipe['dish_name']}\n\n"
            header += _("📊 Nutritional value (per 100g):") + "\n"
            header += _("🔸 Calories: {calories} kcal").format(calories=recipe['nutritional_info']['calories']) + "\n"
            header += _("🔸 Protein: {protein}g").format(protein=recipe['nutritional_info']['protein']) + "\n"
            header += _("🔸 Fats: {fats}g").format(fats=recipe['nutritional_info']['fats']) + "\n"
            header += _("🔸 Carbohydrates: {carbs}g").format(carbs=recipe['nutritional_info']['carbs']) + "\n"
            
            ingredients = _("📝 Ingredients:") + "\n"
            for i, ingredient in enumerate(recipe['ingredients'], 1):
                if ingredient not in ['recipe', 'nutritional_info']:
                    ingredients += f"{i}. {ingredient}\n"
            
            cooking = _("👨‍🍳 Preparation method:") + "\n"
            for i, step in enumerate(recipe['recipe'], 1):
                cooking += f"{i}. {step}\n"
            
            await callback.message.edit_caption(caption=header, reply_markup=None)
            await callback.message.answer(ingredients)
            await callback.message.answer(cooking, reply_markup=await home_kb(user_id=user_id))
    except GeminiApiError:
        await callback.message.edit_caption(
            caption=_("An unexpected API error occurred. Please try again."),
            reply_markup=await back_home_kb(user_id=user_id)
        )
    
    await state.clear()

@start_callback_router.callback_query(F.data == 'find_food_swap')
async def find_food_swap(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback.from_user.id
    _ = await get_user_translator(user_id, callback)
    await callback.answer()
    file_bytes, input_file = await get_image_data(callback.message, bot)

    await state.set_state(UserStates.waiting_for_food_swap)
    await state.update_data(image_bytes=file_bytes)
    
    answer = await callback.message.answer_photo(
        caption=_("Specify which ingredients you'd like to replace with lower-calorie alternatives.\nFor example: \"replace butter, sour cream, and sugar\" or \"all ingredients\"."),
        photo=input_file,
        reply_markup=await cancel_kb(user_id=user_id)
    )
    
    await state.update_data(original_message_id=answer.message_id)

@start_callback_router.callback_query(F.data == 'cancel')
async def cancel_recipe(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    _ = await get_user_translator(callback.from_user.id, callback)
    match current_state:
        case UserStates.waiting_for_recipe:
            await state.clear()
            await callback.answer(_("Recipe search cancelled."))
            await callback.message.delete()
        case UserStates.waiting_for_food_swap:
            await state.clear()
            await callback.answer(_("Alternative search cancelled."))
            await callback.message.delete()
        case _:
            await callback.answer()
            await callback.message.delete()