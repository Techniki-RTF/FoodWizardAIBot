from re import match
from utils.locales import get_user_translator

async def goal_converter(goal, user_id):
    _ = await get_user_translator(user_id)
    match goal:
        case 'lose_weight': return _("Weight Loss")
        case 'maintain_weight': return _("Weight Maintenance")
        case 'mass_gain': return _("Mass Gain")
        case _: return goal

async def user_sex_converter(sex, user_id):
    _ = await get_user_translator(user_id)
    match sex:
        case 'male': return _('Male')
        case 'female': return _('Female')
        case _: return sex

async def params_converter(param, user_id):
    _ = await get_user_translator(user_id)
    match param:
        case 'c_height': return _("181.5 (cm)")
        case 'c_weight': return _("54.2 (kg)")
        case 'c_age': return _("19 (years)")
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


async def bmi_converter(bmi, user_id):
    _ = await get_user_translator(user_id)

    try:
        bmi_value = float(bmi) if bmi else 0
    except (ValueError, TypeError):
        return _('no data')

    match bmi_value:
        case _ if bmi_value < 18.5:
            return f'{bmi} - {_("Underweight")}'
        case _ if 18.5 <= bmi_value < 24.9:
            return f'{bmi} - {_("Normal weight")}'
        case _ if 25 <= bmi_value < 29.9:
            return f'{bmi} - {_("Overweight")}'
        case _ if bmi_value >= 30:
            return f'{bmi} - {_("Obesity")}'
        case _:
            return _('no data')


async def bmi_to_goal_converter(bmi, user_id):
    _ = await get_user_translator(user_id)

    try:
        bmi_value = float(bmi) if bmi else 0
    except (ValueError, TypeError):
        return ''

    string = _('\nFor your BMI {bmi} the recommended goal is ').format(bmi=bmi)
    match bmi_value:
        case _ if 0 < bmi_value < 18.5:
            return string + _("Mass Gain")
        case _ if 18.5 <= bmi_value < 24.9:
            return string + _("Weight Maintenance")
        case _ if bmi_value >= 25:
            return string + _("Weight Loss")
        case _:
            return ''


async def activity_converter(activity, user_id):
    _ = await get_user_translator(user_id)
    match activity:
        case 0: return _('No activity')
        case 1: return _('Light activity')
        case 2: return _('Moderate activity')
        case 3: return _('High activity')
        case 4: return _('Very high activity')
        case _: return _('no data')