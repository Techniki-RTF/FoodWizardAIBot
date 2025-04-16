import io
import json

from aiogram import F, Router, Bot
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from handlers.commands import cmd_start
from states import UserStates
from utils.nutrition_gemini import generate_nutrition

start_msg_router = Router()

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

    response = json.loads(generate_nutrition(file_bytes))
    dish_data = [(dish['dish'], dish['weight'], dish['calories_per_100g'], dish['calories_per_total']) for dish in response['dishes']]
    output = ''
    for dish_name, dish_weight, dish_calories_per_100g, dish_total_calories in dish_data:
        output += f"Название блюда: {dish_name}\nВес: {dish_weight}г\nКалории (100г): {dish_calories_per_100g} ккал\nКалории ({dish_weight}г): {dish_total_calories} ккал\n\n"

    if original_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=original_message_id)
    else:
        pass
    await message.answer_photo(photo=input_file, caption=f'{output}')
    await cmd_start(message)
