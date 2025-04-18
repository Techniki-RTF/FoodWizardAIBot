import io

from aiogram import F, Router, Bot
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from keyboards.inline_keyboard import back_home_kb
from handlers.commands import cmd_start
from states import UserStates
from utils.converters import param_input_converter
from utils.nutrition_gemini import generate_nutrition
from db_handler.database import change_param

start_msg_router = Router()

async def delete_original_message(original_message_id, bot, message):
    if original_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=original_message_id)
    else:
        pass

@start_msg_router.message(F.photo, UserStates.waiting_for_image)
async def handle_image(message: Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    original_message_id = state_data.get('original_message_id')

    image = message.photo[-1]
    file_info = await bot.get_file(image.file_id)

    buffer = io.BytesIO()
    await bot.download_file(file_info.file_path, destination=buffer)
    buffer.seek(0)

    file_bytes = buffer.getvalue()
    file_name = f"{message.message_id}_{image.file_unique_id}.png"
    input_file = BufferedInputFile(file=file_bytes, filename=file_name)

    await state.clear()
    await message.delete()
    await delete_original_message(original_message_id, bot, message)

    response = generate_nutrition(file_bytes)
    if not response:
        await message.answer(text='Не удалось распознать еду на фото, попробуйте другое изображение')
    else:
        dish_data = [(dish['dish'], dish['weight'], dish['calories_per_100g'], dish['calories_per_total']) for dish in response['dishes']]
        output = ''
        for dish_name, dish_weight, dish_calories_per_100g, dish_total_calories in dish_data:
            output += f"Название блюда: {dish_name}\nВес: {dish_weight}г\nКалории (100г): {dish_calories_per_100g} ккал\nКалории ({dish_weight}г): {dish_total_calories} ккал\n\n"
        await message.answer_photo(photo=input_file, caption=f'{output}')
    await cmd_start(message)

@start_msg_router.message(UserStates.waiting_for_param)
async def handle_param(message: Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    original_message_id = state_data.get('original_message_id')
    param = state_data.get('param')
    output = param_input_converter(message.text, param)
    await delete_original_message(original_message_id, bot, message)
    await message.delete()
    if not output:
        await message.answer(text='Неверный формат ввода данных', reply_markup=back_home_kb())
    else:
        await change_param(message.from_user.id, param, output)
        await message.answer(text='Параметр успешно установлен!', reply_markup=back_home_kb())
    await state.clear()