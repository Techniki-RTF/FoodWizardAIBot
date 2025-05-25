from utils.converters import goal_converter
from utils.locales import get_user_translator

activity_multipliers = {"0": 1.2, "1": 1.375, "2": 1.55, "3": 1.725, "4": 1.9}


# noinspection PyUnboundLocalVariable
async def msj_equation(c_profile, activity, user_id):
    _ = await get_user_translator(user_id)
    weight, height, age, sex, goal = (
        c_profile['weight'], c_profile['height'], c_profile['age'], c_profile['sex'], c_profile['goal'])
    if None in (weight, height, age, sex):
        return [_("Insufficient data.\nPlease complete your profile."), None]
    match sex:
        case 'male': x = 5
        case 'female': x = -161
    bmr = int((10 * weight + 6.25 * height - 5 * age + x) * activity_multipliers[activity])
    response, multiplied_bmr = await goal_multiplier(bmr, goal, user_id)
    return [_('Your daily calorie allowance: {bmr} kcal').format(bmr=bmr) + response, multiplied_bmr]

async def goal_multiplier(bmr, goal, user_id):
    _ = await get_user_translator(user_id)
    match goal:
        case "lose_weight": 
            bmr *= 0.85
            return [_('\nConsidering your goal ({goal}): {bmr} kcal').format(goal=await goal_converter(goal, user_id), bmr=int(bmr)), bmr]
        case "mass_gain": 
            bmr *= 1.15
            return [_('\nConsidering your goal ({goal}): {bmr} kcal').format(goal=await goal_converter(goal, user_id), bmr=int(bmr)), bmr]
        case _: 
            return ['', bmr]