from re import match

def goal_converter(goal):
    match goal:
        case 'lose_weight': return "Похудение"
        case 'maintain_weight': return "Поддержание веса"
        case 'mass_gain': return "Набор массы"
        case _: return goal

def user_sex_converter(sex):
    match sex:
        case 'male': return 'Мужской'
        case 'female': return 'Женский'
        case _: return sex

def params_converter(param):
    match param:
        case 'c_height': return "181.5 (см)"
        case 'c_weight': return "54.2 (кг)"
        case 'c_age': return "19 (лет)"
        case _: return None

def param_input_converter(user_input, param):
    if not match(r'^[+]?[0-9]*\.?[0-9]+$', user_input):
        return False
    user_input = float(user_input)
    match param:
        case 'c_weight':
            if not 30 <= user_input <= 150: return False
        case 'c_height':
            if not 100 <= user_input <= 250: return False
        case 'c_age':
            user_input = int(user_input)
            if not 14 <= user_input <= 120: return False
    return user_input

def bmi_converter(bmi):
    match bmi:
        case _ if 0 < bmi < 18.5: return f'{bmi} - Недостаточный вес'
        case _ if 18.5 <= bmi < 24.9: return f'{bmi} - Нормальный вес'
        case _ if 25 <= bmi < 29.9: return f'{bmi} - Избыточный вес'
        case _ if bmi >= 30: return f'{bmi} - Ожирение'
        case _: return 'нет данных'

def bmi_to_goal_converter(bmi):
    string = f'\nПри вашем ИМТ {bmi} рекомендуемая цель - '
    match bmi:
        case _ if 0 < bmi < 18.5: return string + 'Набор массы'
        case _ if 18.5 <= bmi < 24.9: return string + 'Поддержание веса'
        case _ if bmi >= 25 : return string + 'Похудение'
        case _: return ''

def activity_converter(activity):
    match activity:
        case 0: return 'Отсутствие активности'
        case 1: return 'Лёгкая активность'
        case 2: return 'Средняя активность'
        case 3: return 'Высокая активность'
        case 4: return 'Очень высокая активность'
        case _: return 'нет данных'