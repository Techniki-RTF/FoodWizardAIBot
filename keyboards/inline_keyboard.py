from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Отправить изображение", callback_data='send_image')],
        [InlineKeyboardButton(text="Профиль", callback_data='profile')],
        [InlineKeyboardButton(text="Рассчитать суточную норму калорий", callback_data='daily_kcal')],
        [InlineKeyboardButton(text="Составить недельный рацион", callback_data='nutrition_plan')],
        [InlineKeyboardButton(text="О боте", callback_data='about')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def image_response_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Отправить новое изображение", callback_data='send_image')],
        [InlineKeyboardButton(text="Найти низкокалорийный рецепт", callback_data='find_recipe')],
        [InlineKeyboardButton(text="Главное меню", callback_data='home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def no_response_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Отправить новое изображение", callback_data='send_image')],
        [InlineKeyboardButton(text="Главное меню", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def home_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Главное меню", callback_data='home')]
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

def goal_kb(bmi = None):
    inline_kb_list = [
        [InlineKeyboardButton(text=f"Похудение {"(Рекомендовано при вашем ИМТ)" if bmi >= 25 else ""}", callback_data='lose_weight')],
        [InlineKeyboardButton(text=f"Поддержание веса {"(Рекомендовано при вашем ИМТ)" if 18.5 <= bmi < 24.9 else ""}", callback_data='maintain_weight')],
        [InlineKeyboardButton(text=f"Набор массы {"(Рекомендовано при вашем ИМТ)" if 0 < bmi < 18.5 else ""}", callback_data='mass_gain')],
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

def daily_kcal_kb(activity = None):
    inline_kb_list = [
    [InlineKeyboardButton(text=f"Отсутствие активности {"(выбрано)" if activity == 0 else ""}", callback_data="activity_0")],
    [InlineKeyboardButton(text=f"Легкая (физ. нагрузки 1-3 раза в неделю) {"(выбрано)" if activity == 1 else ""}", callback_data="activity_1")],
    [InlineKeyboardButton(text=f"Средняя (физ. нагрузки 3-5 раз в неделю) {"(выбрано)" if activity == 2 else ""}", callback_data="activity_2")],
    [InlineKeyboardButton(text=f"Высокая (физ. нагрузки 6-7 раз в неделю) {"(выбрано)" if activity == 3 else ""}", callback_data="activity_3")],
    [InlineKeyboardButton(text=f"Очень высокая (постоянная физ. нагрузка) {"(выбрано)" if activity == 4 else ""}", callback_data="activity_4")],
        [InlineKeyboardButton(text=f"На главную", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def back_activity_kb():
    inline_kb_list = [[InlineKeyboardButton(text="Назад", callback_data='daily_kcal')]]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def back_param_kb(success = True):
    inline_kb_list = [[InlineKeyboardButton(text="Задать остальные параметры" if success else "Попробовать снова", callback_data='params')],
                      [InlineKeyboardButton(text="На главную", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def retry_plan_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Попробовать снова", callback_data='nutrition_plan')],
        [InlineKeyboardButton(text="На главную", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def recipe_list_kb(dishes):
    inline_kb_list = [[InlineKeyboardButton(text="Отмена", callback_data='cancel')]]
    for dish in dishes:
        inline_kb_list.insert(0, [InlineKeyboardButton(text=dish, callback_data=f'recipe_{dish}')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
