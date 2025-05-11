from utils.converters import goal_converter

activity_multipliers = {"0": 1.2, "1": 1.375, "2": 1.55, "3": 1.725, "4": 1.9}


# noinspection PyUnboundLocalVariable
def msj_equation(c_profile, activity):
    weight, height, age, sex, goal = (
        c_profile['weight'], c_profile['height'], c_profile['age'], c_profile['sex'], c_profile['goal'])
    if None in (weight, height, age, sex):
        return 'Недостаточно данных.\nЗаполните профиль, пожалуйста.'
    match sex:
        case 'male': x = 5
        case 'female': x = -161
    bmr = int((10 * weight + 6.25 * height - 5 * age + x) * activity_multipliers[activity])
    response, multiplied_bmr,  = goal_multiplier(bmr, goal)
    return [f'Ваша суточная норма калорий: {bmr} ккал{response}', multiplied_bmr]

def goal_multiplier(bmr, goal):
    match goal:
        case "lose_weight": bmr *= 0.85
        case "mass_gain": bmr *= 1.15
        case _: return ''
    return [f'\nС учётом вашей цели ({goal_converter(goal)}): {int(bmr)} ккал', bmr]