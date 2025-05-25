from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.locales import get_user_translator

async def main_menu_kb(user_id=None):
    _ = await get_user_translator(user_id) if user_id else lambda x: x
    inline_kb_list = [
        [InlineKeyboardButton(text=_("Send Image"), callback_data='send_image')],
        [InlineKeyboardButton(text=_("Profile"), callback_data='profile')],
        [InlineKeyboardButton(text=_("Calculate Daily Calorie Allowance"), callback_data='daily_kcal')],
        [InlineKeyboardButton(text=_("Create Weekly Meal Plan"), callback_data='nutrition_plan')],
        [InlineKeyboardButton(text=_("About Bot"), callback_data='about')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def image_response_kb(user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [
        [InlineKeyboardButton(text=_("Send New Image"), callback_data='send_image')],
        [InlineKeyboardButton(text=_("Find Low-Calorie Recipe"), callback_data='find_recipe')],
        [InlineKeyboardButton(text=_("Find Low-Calorie Food Alternatives"), callback_data='find_food_swap')],
        [InlineKeyboardButton(text=_("Main Menu"), callback_data='home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def no_response_kb(user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [
        [InlineKeyboardButton(text=_("Send New Image"), callback_data='send_image')],
        [InlineKeyboardButton(text=_("Main Menu"), callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def home_kb(user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [
        [InlineKeyboardButton(text=_("Main Menu"), callback_data='home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def back_home_kb(user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [
        [InlineKeyboardButton(text=_("To Main Menu"), callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def profile_kb(user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [
        [InlineKeyboardButton(text=_("Change Goal"), callback_data='goal')],
        [InlineKeyboardButton(text=_("Change Sex"), callback_data='sex')],
        [InlineKeyboardButton(text=_("Change Personal Parameters"), callback_data='params')],
        [InlineKeyboardButton(text=_("Change language"), callback_data='lang')],
        [InlineKeyboardButton(text=_("To Main Menu"), callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def goal_kb(user_id, bmi=None):
    _ = await get_user_translator(user_id)
    inline_kb_list = [
        [InlineKeyboardButton(text=_("Weight Loss") + (f" ({_('Recommended for your BMI')})" if bmi and bmi >= 25 else ""), callback_data='lose_weight')],
        [InlineKeyboardButton(text=_("Weight Maintenance") + (f" ({_('Recommended for your BMI')})" if bmi and 18.5 <= bmi < 24.9 else ""), callback_data='maintain_weight')],
        [InlineKeyboardButton(text=_("Mass Gain") + (f" ({_('Recommended for your BMI')})" if bmi and 0 < bmi < 18.5 else ""), callback_data='mass_gain')],
        [InlineKeyboardButton(text=_("Back"), callback_data='profile')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def user_sex_kb(user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [
        [InlineKeyboardButton(text=_("Male"), callback_data='male')],
        [InlineKeyboardButton(text=_("Female"), callback_data='female')],
        [InlineKeyboardButton(text=_("Back"), callback_data='profile')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def params_kb(user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [
        [InlineKeyboardButton(text=_("Change Height"), callback_data='c_height')],
        [InlineKeyboardButton(text=_("Change Weight"), callback_data='c_weight')],
        [InlineKeyboardButton(text=_("Change Age"), callback_data='c_age')],
        [InlineKeyboardButton(text=_("Back"), callback_data='profile')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def back_kb(callback, user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [[InlineKeyboardButton(text=_("Back"), callback_data=f'{callback}')]]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def lang_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Русский", callback_data='ru')],
        [InlineKeyboardButton(text="English", callback_data='en')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def daily_kcal_kb(user_id, activity=None):
    _ = await get_user_translator(user_id)
    inline_kb_list = [
        [InlineKeyboardButton(text=_("No activity") + (f" ({_('selected')})" if activity == 0 else ""), callback_data="activity_0")],
        [InlineKeyboardButton(text=_("Light (physical activity 1-3 times a week)") + (f" ({_('selected')})" if activity == 1 else ""), callback_data="activity_1")],
        [InlineKeyboardButton(text=_("Moderate (physical activity 3-5 times a week)") + (f" ({_('selected')})" if activity == 2 else ""), callback_data="activity_2")],
        [InlineKeyboardButton(text=_("High (physical activity 6-7 times a week)") + (f" ({_('selected')})" if activity == 3 else ""), callback_data="activity_3")],
        [InlineKeyboardButton(text=_("Very high (constant physical activity)") + (f" ({_('selected')})" if activity == 4 else ""), callback_data="activity_4")],
        [InlineKeyboardButton(text=_("To Main Menu"), callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def back_activity_kb(user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [[InlineKeyboardButton(text=_("Back"), callback_data='daily_kcal')]]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def back_param_kb(user_id, success=True):
    _ = await get_user_translator(user_id)
    inline_kb_list = [
        [InlineKeyboardButton(text=_("Set other parameters") if success else _("Try Again"), callback_data='params')],
        [InlineKeyboardButton(text=_("To Main Menu"), callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def retry_plan_kb(user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [
        [InlineKeyboardButton(text=_("Try Again"), callback_data='nutrition_plan')],
        [InlineKeyboardButton(text=_("To Main Menu"), callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def recipe_list_kb(dishes, user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [[InlineKeyboardButton(text=_("Cancel"), callback_data='cancel')]]
    for dish in dishes:
        inline_kb_list.insert(0, [InlineKeyboardButton(text=dish, callback_data=f'recipe_{dish}')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

async def cancel_kb(user_id):
    _ = await get_user_translator(user_id)
    inline_kb_list = [[InlineKeyboardButton(text=_("Cancel"), callback_data='cancel')]]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
