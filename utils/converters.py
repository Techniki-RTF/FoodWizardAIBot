from re import match

def goal_converter(goal):
    match goal:
        case 'lose_weight': return "Похудение"
        case 'maintain_weight': return "Поддержание веса"
        case 'mass_gain': return "Набор массы"
        case _: return None

def user_sex_converter(sex):
    match sex:
        case 'male': return 'Мужской'
        case 'female': return 'Женский'
        case _: return None

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