import os

from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.inline_keyboard import back_home_kb
from states import UserStates

start_msg_router = Router()

@start_msg_router.message(F.photo, UserStates.waiting_for_image)
async def handle_image(message: Message, state: FSMContext, bot: Bot):

    image = message.photo[-1]
    folder = "images"
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_info = await bot.get_file(image.file_id)
    file_name = os.path.join(folder, f"{message.message_id}_{image.file_unique_id}.jpg")
    await bot.download_file(file_info.file_path, destination=file_name)

    await state.clear()

    if original_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=original_message_id)
    else:
        pass
    await message.answer_photo(photo=input_file, caption=f'{file_name}', reply_markup=back_home_kb())