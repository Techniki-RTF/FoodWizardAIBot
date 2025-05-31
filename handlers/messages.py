import io
from datetime import datetime
from decouple import config

from aiogram import F, Router, Bot
from aiogram.types import Message, BufferedInputFile, MessageReactionUpdated
from aiogram.fsm.context import FSMContext

from keyboards.inline_keyboard import *
from states import UserStates
from utils.converters import param_input_converter, goal_converter
from utils.gemini import generate_nutrition_plan, generate_food_swap
from utils.nutrition import get_output
from db_handler.database import change_param, get_db, get_profile, get_user_lang
from aiogram.exceptions import TelegramBadRequest
from utils.locales import get_user_translator

start_msg_router = Router()

async def delete_original_message(original_message_id, bot, message):
    if original_message_id:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=original_message_id)
        except TelegramBadRequest:
            pass
    else:
        pass

@start_msg_router.message(F.photo, UserStates.waiting_for_image)
async def handle_image(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    _ = await get_user_translator(user_id)
    
    state_data = await state.get_data()

    image = message.photo[-1]
    file_info = await bot.get_file(image.file_id)

    buffer = io.BytesIO()
    await bot.download_file(file_info.file_path, destination=buffer)
    buffer.seek(0)

    file_bytes = buffer.getvalue()
    file_name = f"{message.message_id}_{image.file_unique_id}.png"
    input_file = BufferedInputFile(file=file_bytes, filename=file_name)

    main_menu_message_id = state_data.get('menu_message_id')
    await state.clear()
    if main_menu_message_id:
        await state.update_data(menu_message_id=main_menu_message_id)

    await message.delete()
    await delete_original_message(state_data.get('original_message_id'), bot, message)

    answer = await message.answer(text=_("Recognizing..."))
    await bot.send_chat_action(message.chat.id, 'upload_photo')
    response = await get_output(file_bytes, user_lang=await get_user_lang(user_id))
    match response:
        case False:
            await answer.edit_text(_("Could not recognize food in the photo. Please try another image."), reply_markup=await no_response_kb(user_id=user_id))
        case 'api_error':
             await answer.edit_text(_("An unexpected error occurred. Please try again."), reply_markup=await no_response_kb(user_id=user_id))
        case _:
            dishes = response.get('dishes', response) if isinstance(response, dict) else response
            dish_data = [(dish['dish_user_lang'], dish['weight'], dish['calories_per_100g'], dish['calories_per_total'], dish['pfc_per_100g'], dish['pfc_per_total']) for dish in dishes]
            output = ''
            for dish_name, dish_weight, dish_calories_per_100g, dish_total_calories, pfc_per_100g, pfc_per_total in dish_data:
                output += (_("Dish name: {dish_name}").format(dish_name=dish_name) + "\n" + 
                           _("Weight: {dish_weight}g").format(dish_weight=dish_weight) + "\n\n" +
                           _("Calories (100g): {dish_calories_per_100g} kcal").format(dish_calories_per_100g=dish_calories_per_100g) + "\n" + 
                           _("Calories ({dish_weight}g): {dish_total_calories} kcal").format(dish_weight=dish_weight, dish_total_calories=dish_total_calories) + "\n\n" +
                           _("PFC (100g): {pfc_per_100g}").format(pfc_per_100g=pfc_per_100g) + "\n" + 
                           _("PFC ({dish_weight}g): {pfc_per_total}").format(dish_weight=dish_weight, pfc_per_total=pfc_per_total) + "\n\n")
            await answer.delete()
            try:
                await message.answer_photo(photo=input_file, caption=f'{output}', reply_markup=await image_response_kb(user_id=user_id))
            except TelegramBadRequest:
                answer = await message.answer_photo(photo=input_file)
                await answer.reply(text=f'{output}', reply_markup=await image_response_kb(user_id=user_id))
@start_msg_router.message(UserStates.waiting_for_param)
async def handle_param(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    _ = await get_user_translator(user_id)
    
    state_data = await state.get_data()
    original_message_id = state_data.get('original_message_id')
    param = state_data.get('param')
    output = param_input_converter(message.text, param)
    if not output:
        await bot.edit_message_text(text=_("Invalid data input format ({text})").format(text=message.text), reply_markup=await back_param_kb(success=False, user_id=user_id), message_id=original_message_id, chat_id=message.chat.id)
    else:
        await change_param(user_id, param, output)
        await bot.edit_message_text(text=_("Parameter set successfully!"), reply_markup=await back_param_kb(user_id=user_id), message_id=original_message_id, chat_id=message.chat.id)
    await message.delete()
    await state.clear()

@start_msg_router.message_reaction()
async def handle_reaction(message_reaction: MessageReactionUpdated, bot: Bot):
    user_id = message_reaction.user.id
    _ = await get_user_translator(user_id)
    
    if user_id == int(config("ADMINS")):
        c_db = await get_db()
        
        cursor = await c_db.execute("PRAGMA table_info(users)")
        columns_info = await cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        query = f"SELECT {', '.join(column_names)} FROM users"
        cursor = await c_db.execute(query)
        rows = await cursor.fetchall()
        
        users_info = []
        for row in rows:
            user_data = []
            for i, value in enumerate(row):
                col_name = column_names[i]
                formatted_value = value if value is not None else _("not specified")
                user_data.append(f"{col_name}: {formatted_value}")
            users_info.append("\n".join(user_data))
        
        all_users_info = "\n\n".join(users_info)
        try:
            await bot.edit_message_text(
                text=_("User data ({datetime}):").format(datetime=datetime.now()) + f"\n\n{all_users_info}",
                message_id=message_reaction.message_id,
                chat_id=message_reaction.chat.id,
                reply_markup=await back_home_kb(user_id=user_id)
            )
        except TelegramBadRequest:
            await bot.send_message(
                chat_id=message_reaction.chat.id,
                text=_("User data ({datetime}):").format(datetime=datetime.now()) + f"\n\n{all_users_info}",
                reply_markup=await back_home_kb(user_id=user_id)
            )


@start_msg_router.message(UserStates.waiting_for_diet_preferences)
async def handle_diet_preferences(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    _ = await get_user_translator(user_id)
    
    preferences = message.text

    state_data = await state.get_data()
    original_message_id = state_data.get('original_message_id')

    await message.delete()
    
    if len(preferences) > 100:
        await bot.edit_message_text(
            text=_("Text too long. Please specify preferences within 100 characters."),
            chat_id=message.chat.id,
            message_id=original_message_id,
            reply_markup=await retry_plan_kb(user_id=user_id)
        )
        return

    c_profile = (await get_profile(user_id))
    await bot.edit_message_text(
        text=_("Creating a meal plan for {daily_kcal} kcal/day...").format(daily_kcal=c_profile['daily_kcal']),
        chat_id=message.chat.id,
        message_id=original_message_id
    )

    await bot.send_chat_action(message.chat.id, 'typing')

    preferences_text = preferences if preferences.lower() != 'нет' else None
    response = await generate_nutrition_plan(daily_kcal=c_profile['daily_kcal'], goal=await goal_converter(c_profile['goal'], user_id),
                                             preferences=preferences_text, user_lang=await get_user_lang(user_id))

    await state.clear()

    match response:
        case 'api_error':
            await bot.edit_message_text(
                text=_("An unexpected API error occurred. Please try again."),
                chat_id=message.chat.id,
                message_id=original_message_id,
                reply_markup=await back_home_kb(user_id=user_id)
            )
        case _:
            days = response.get('days', [])
            if not days:
                await bot.edit_message_text(
                    text=_("Failed to create a meal plan. Please try again."),
                    chat_id=message.chat.id,
                    message_id=original_message_id,
                    reply_markup=await back_home_kb(user_id=user_id)
                )
                return

            full_plan = _("🍽️ Weekly meal plan ({daily_kcal} kcal/day)").format(daily_kcal=c_profile['daily_kcal'])
            if preferences_text:
                full_plan += "\n" + _("📝 Considering preferences: {preferences}").format(preferences=preferences_text)
            full_plan += "\n\n"

            for day in days:
                day_name = day['day_name'].capitalize()
                day_calories = day['calories']
                day_proteins = day['proteins']
                day_fats = day['fats']
                day_carbs = day['carbs']

                full_plan += _("📅 {day_name} (P: {day_proteins}g, F: {day_fats}g, C: {day_carbs}g, {day_calories} kcal)").format(
                    day_name=day_name, 
                    day_proteins=day_proteins, 
                    day_fats=day_fats, 
                    day_carbs=day_carbs, 
                    day_calories=day_calories
                ) + "\n\n"

                breakfast = day['breakfast'][0]
                full_plan += _("🍳 Breakfast: {breakfast_dish}").format(breakfast_dish=breakfast['dish_name']) + "\n"
                full_plan += f"{breakfast['description']}\n"
                full_plan += _("P: {breakfast_proteins}g, F: {breakfast_fats}g, C: {breakfast_carbs}g, {breakfast_calories} kcal").format(
                    breakfast_proteins=breakfast['proteins'],
                    breakfast_fats=breakfast['fats'],
                    breakfast_carbs=breakfast['carbs'],
                    breakfast_calories=breakfast['calories']
                ) + "\n\n"

                lunch = day['lunch'][0]
                full_plan += _("🥗 Lunch: {lunch_dish}").format(lunch_dish=lunch['dish_name']) + "\n"
                full_plan += f"{lunch['description']}\n"
                full_plan += _("P: {lunch_proteins}g, F: {lunch_fats}g, C: {lunch_carbs}g, {lunch_calories} kcal").format(
                    lunch_proteins=lunch['proteins'],
                    lunch_fats=lunch['fats'],
                    lunch_carbs=lunch['carbs'],
                    lunch_calories=lunch['calories']
                ) + "\n\n"

                dinner = day['dinner'][0]
                full_plan += _("🍲 Dinner: {dinner_dish}").format(dinner_dish=dinner['dish_name']) + "\n"
                full_plan += f"{dinner['description']}\n"
                full_plan += _("P: {dinner_proteins}g, F: {dinner_fats}g, C: {dinner_carbs}g, {dinner_calories} kcal").format(
                    dinner_proteins=dinner['proteins'],
                    dinner_fats=dinner['fats'],
                    dinner_carbs=dinner['carbs'],
                    dinner_calories=dinner['calories']
                ) + "\n\n"

                full_plan += "➖➖➖➖➖➖➖➖➖➖➖➖\n\n"

            full_plan += _("Comments from the neural network: {commentary}").format(commentary=response.get('commentary', []))

            await bot.delete_message(chat_id=message.chat.id, message_id=original_message_id)
            await message.answer(full_plan, reply_markup=await home_kb(user_id=user_id))

@start_msg_router.message(UserStates.waiting_for_food_swap)
async def handle_food_swap(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    _ = await get_user_translator(user_id)
    
    food_to_swap = message.text

    state_data = await state.get_data()
    original_message_id = state_data.get('original_message_id')
    file_bytes = state_data.get('file_bytes')

    await message.delete()
    
    if len(food_to_swap) > 100:
        await bot.edit_message_caption(
            caption=_("Text too long. Please list ingredients within 100 characters."),
            chat_id=message.chat.id,
            message_id=original_message_id,
            reply_markup=await back_home_kb(user_id=user_id)
        )
        return

    await bot.edit_message_caption(
        caption=_("Searching for low-calorie alternatives..."),
        chat_id=message.chat.id,
        message_id=original_message_id,
        reply_markup=None
    )

    await bot.send_chat_action(message.chat.id, 'typing')

    response = await generate_food_swap([food_to_swap], file_bytes, user_lang=await get_user_lang(user_id))

    await state.clear()

    match response:
        case 'api_error':
            await bot.edit_message_caption(
                caption=_("An unexpected API error occurred. Please try again."),
                chat_id=message.chat.id,
                message_id=original_message_id,
                reply_markup=await back_home_kb(user_id=user_id)
            )
        case _:
            result = _("🔄 Low-calorie alternatives for ingredients:") + "\n\n"
            
            for item in response['swapped']:
                result += f"{item['original_ingredient']} ➡️ {item['alternative']}\n\n"
                result += f"{item['description']}\n"
                
                nutrition = item['nutritional_info']
                
                if nutrition['calories'] and nutrition['calories_old']:
                    cal_diff = nutrition['calories_old'] - nutrition['calories']
                    cal_percent = round((cal_diff / nutrition['calories_old']) * 100)
                    result += _("Calories: {calories} kcal instead of {calories_old} kcal (-{cal_diff} kcal, -{cal_percent}%)").format(
                        calories=nutrition['calories'],
                        calories_old=nutrition['calories_old'],
                        cal_diff=cal_diff,
                        cal_percent=cal_percent
                    ) + "\n\n"
                
                if nutrition['protein'] or nutrition['fats'] or nutrition['carbs']:
                    result += _("PFC difference (per 100g): P: {protein}g, F: {fats}g, C: {carbs}g").format(
                        protein=nutrition['protein'],
                        fats=nutrition['fats'],
                        carbs=nutrition['carbs']
                    ) + "\n\n"
            
            await bot.edit_message_caption(
                caption=result,
                chat_id=message.chat.id,
                message_id=original_message_id,
                reply_markup=await home_kb(user_id=user_id)
            )