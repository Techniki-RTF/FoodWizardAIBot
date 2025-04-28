import io
from datetime import datetime
from decouple import config

from aiogram import F, Router, Bot
from aiogram.types import Message, BufferedInputFile, MessageReactionUpdated
from aiogram.fsm.context import FSMContext

from keyboards.inline_keyboard import back_home_kb, image_response_kb, no_response_kb
from states import UserStates
from utils.converters import param_input_converter
from utils.nutrition import get_output
from db_handler.database import change_param, get_db

start_msg_router = Router()

async def delete_original_message(original_message_id, bot, message):
    if original_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=original_message_id)
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
            dish_data = [(dish['dish_ru'], dish['weight'], dish['calories_per_100g'], dish['calories_per_total']) for dish in response['dishes']]
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
        cursor = await c_db.execute('SELECT user_id, height, weight, age, sex, goal, bmi, created_at FROM users')
        rows = await cursor.fetchall()
        users_info = "\n\n".join([f"👤 ID: {row[0]}\n📏 Рост: {row[1] or 'не указан'} см\n⚖️ Вес: {row[2] or 'не указан'} кг\n🔢 Возраст: {row[3] or 'не указан'}\n👫 Пол: {row[4] or 'не указан'}\n🎯 Цель: {row[5] or 'не указана'}\n📈 ИМТ: {row[6] or 'не указан'}\n📅 Создан: {row[7]}\n" for row in rows])
        await bot.edit_message_text(text=f"📊 Данные пользователей ({datetime.now()}):\n\n{users_info}", message_id=message_reaction.message_id, chat_id=message_reaction.chat.id, reply_markup=back_home_kb())
