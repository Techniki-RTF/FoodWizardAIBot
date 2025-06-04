from aiogram.exceptions import TelegramBadRequest


async def delete_menu_message(message, current_state, bot):
    data = await current_state.get_data()
    menu_message_id = data.get('menu_message_id')
    if menu_message_id:
        try:
            await bot.delete_message(message.chat.id, menu_message_id)
        except TelegramBadRequest:
            pass