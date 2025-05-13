from aiogram.fsm.state import StatesGroup, State

class UserStates(StatesGroup):
    waiting_for_image = State()
    waiting_for_param = State()
    waiting_for_diet_preferences = State()
    waiting_for_food_swap = State()
    waiting_for_recipe = State()