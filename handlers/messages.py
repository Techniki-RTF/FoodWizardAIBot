import io
from datetime import datetime
from decouple import config

from aiogram import F, Router, Bot
from aiogram.types import Message, BufferedInputFile, MessageReactionUpdated
from aiogram.fsm.context import FSMContext

from keyboards.inline_keyboard import back_home_kb, image_response_kb, no_response_kb, home_kb, retry_plan_kb
from states import UserStates
from utils.converters import param_input_converter, goal_converter
from utils.gemini import generate_nutrition_plan
from utils.nutrition import get_output
from db_handler.database import change_param, get_db, get_profile
from aiogram.exceptions import TelegramBadRequest

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

    answer = await message.answer(text='Распознавание в процессе...')
    await bot.send_chat_action(message.chat.id, 'upload_photo')
    response = await get_output(file_bytes)
    match response:
        case False:
            await answer.edit_text('Не удалось распознать еду на фото, попробуйте другое изображение', reply_markup=no_response_kb())
        case 'api_error':
             await answer.edit_text('Произошла непредвиденная ошибка, попробуйте ещё раз', reply_markup=no_response_kb())
        case _:
            dishes = response.get('dishes', response) if isinstance(response, dict) else response
            dish_data = [(dish['dish_ru'], dish['weight'], dish['calories_per_100g'], dish['calories_per_total']) for dish in dishes]
            output = ''
            for dish_name, dish_weight, dish_calories_per_100g, dish_total_calories in dish_data:
                output += f"Название блюда: {dish_name}\nВес: {dish_weight}г\nКалории (100г): {dish_calories_per_100g} ккал\nКалории ({dish_weight}г): {dish_total_calories} ккал\n\n"
            await answer.delete()
            await message.answer_photo(photo=input_file, caption=f'{output}', reply_markup=image_response_kb())

@start_msg_router.message(UserStates.waiting_for_param)
async def handle_param(message: Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    original_message_id = state_data.get('original_message_id')
    param = state_data.get('param')
    output = param_input_converter(message.text, param)
    if not output:
        await bot.edit_message_text(text=f'Неверный формат ввода данных ({message.text})', reply_markup=back_home_kb(), message_id=original_message_id, chat_id=message.chat.id)
    else:
        await change_param(message.from_user.id, param, output)
        await bot.edit_message_text(text='Параметр успешно установлен!', reply_markup=back_home_kb(), message_id=original_message_id, chat_id=message.chat.id)
    await message.delete()
    await state.clear()

@start_msg_router.message_reaction()
async def handle_reaction(message_reaction: MessageReactionUpdated, bot: Bot):
    if message_reaction.user.id == int(config("ADMINS")):
        c_db = get_db()
        
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
                formatted_value = value if value is not None else 'не указан'
                user_data.append(f"{col_name}: {formatted_value}")
            users_info.append("\n".join(user_data))
        
        all_users_info = "\n\n".join(users_info)
        try:
            await bot.edit_message_text(
                text=f"Данные пользователей ({datetime.now()}):\n\n{all_users_info}",
                message_id=message_reaction.message_id,
                chat_id=message_reaction.chat.id,
                reply_markup=back_home_kb()
            )
        except TelegramBadRequest:
            await bot.send_message(
                chat_id=message_reaction.chat.id,
                text=f"Данные пользователей ({datetime.now()}):\n\n{all_users_info}",
                reply_markup=back_home_kb()
            )


@start_msg_router.message(UserStates.waiting_for_diet_preferences)
async def handle_diet_preferences(message: Message, state: FSMContext, bot: Bot):
    preferences = message.text
    user_id = message.from_user.id

    state_data = await state.get_data()
    original_message_id = state_data.get('original_message_id')

    await message.delete()
    
    if len(preferences) > 100:
        await bot.edit_message_text(
            text="Слишком длинный текст. Пожалуйста, укажите предпочтения не более 100 символов.",
            chat_id=message.chat.id,
            message_id=original_message_id,
            reply_markup=retry_plan_kb()
        )
        return

    c_profile = (await get_profile(user_id))
    await bot.edit_message_text(
        text=f"План питания на {c_profile['daily_kcal']} ккал в день создаётся...",
        chat_id=message.chat.id,
        message_id=original_message_id
    )

    await bot.send_chat_action(message.chat.id, 'typing')

    preferences_text = preferences if preferences.lower() != 'нет' else None
    response = await generate_nutrition_plan(c_profile['daily_kcal'], goal_converter(c_profile['goal']), preferences_text)

    await state.clear()

    match response:
        case 'api_error':
            await bot.edit_message_text(
                text='Произошла непредвиденная ошибка, попробуйте ещё раз',
                chat_id=message.chat.id,
                message_id=original_message_id,
                reply_markup=back_home_kb()
            )
        case _:
            days = response.get('days', [])
            if not days:
                await bot.edit_message_text(
                    text='Не удалось составить план питания, попробуйте ещё раз',
                    chat_id=message.chat.id,
                    message_id=original_message_id,
                    reply_markup=back_home_kb()
                )
                return

            full_plan = f"🍽️ План питания на неделю ({c_profile['daily_kcal']} ккал/день)"
            if preferences_text:
                full_plan += f"\n📝 С учетом предпочтений: {preferences_text}"
            full_plan += "\n\n"

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

            full_plan += f"Комментарии от нейросети: {response.get('commentary', [])}"

            await bot.delete_message(chat_id=message.chat.id, message_id=original_message_id)
            await message.answer(full_plan, reply_markup=home_kb())