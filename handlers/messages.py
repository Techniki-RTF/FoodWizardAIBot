import io

from aiogram import F, Router, Bot
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from keyboards.inline_keyboard import back_home_kb
from states import UserStates

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
    file_name = f"{message.message_id}_{image.file_unique_id}.jpg"
    input_file = BufferedInputFile(file=file_bytes, filename=file_name)

    await state.clear()
    await message.delete()

    if original_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=original_message_id)
    else:
        pass
    await message.answer_photo(photo=input_file, caption=f'{file_name}', reply_markup=back_home_kb())