from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Отправить изображение", callback_data='send_image')],
        [InlineKeyboardButton(text="Профиль", callback_data='profile')],
        [InlineKeyboardButton(text="О боте", callback_data='about')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def image_response_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Отправить новое изображение", callback_data='send_image')],
        [InlineKeyboardButton(text="Главное меню", callback_data='home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def no_response_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Отправить новое изображение", callback_data='send_image')],
        [InlineKeyboardButton(text="Главное меню", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def back_home_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="На главную", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def profile_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Изменить цель", callback_data='goal')],
        [InlineKeyboardButton(text="Изменить пол", callback_data='sex')],
        [InlineKeyboardButton(text="Изменить личные параметры", callback_data='params')],
        [InlineKeyboardButton(text="На главную", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def goal_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Похудение", callback_data='lose_weight')],
        [InlineKeyboardButton(text="Поддержание веса", callback_data='maintain_weight')],
        [InlineKeyboardButton(text="Набор массы", callback_data='gain_mass')],
        [InlineKeyboardButton(text="Назад", callback_data='profile')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def user_sex_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Мужской", callback_data='male')],
        [InlineKeyboardButton(text="Женский", callback_data='female')],
        [InlineKeyboardButton(text="Назад", callback_data='profile')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def params_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Изменить рост", callback_data='c_height')],
        [InlineKeyboardButton(text="Изменить вес", callback_data='c_weight')],
        [InlineKeyboardButton(text="Изменить возраст", callback_data='c_age')],
        [InlineKeyboardButton(text="Назад", callback_data='profile')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def back_params_kb():
    inline_kb_list = [[InlineKeyboardButton(text="Назад", callback_data='params')]]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)