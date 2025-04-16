def goal_converter(goal):
    match goal:
        case 'lose_weight': return "похудение"
        case 'maintain_weight': return "поддержание веса"
        case 'gain_mass': return "набор массы"
        case _: return None

def params_converter(param):
    match param:
        case 'c_height': return "181.5 (см)"
        case 'c_weight': return "54.2 (кг)"
        case 'c_age': return "19 (лет)"
        case _: return None