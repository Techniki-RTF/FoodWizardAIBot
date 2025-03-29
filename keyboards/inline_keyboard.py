from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Отправить изображение", callback_data='send_image')],
        [InlineKeyboardButton(text="О боте", callback_data='about')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)



def back_home_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="На главную", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)