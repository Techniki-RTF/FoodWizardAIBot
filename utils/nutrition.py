import json

from utils.gemini import recognize_dish, get_final_output
from utils.calorie_ninjas import get_nutrition_info

async def get_output(image_bytes):
    gemini_output = await recognize_dish(image_bytes)
    print(f'gemini_output: {gemini_output}')
    dishes = gemini_output['dishes']
    dish_names = [dish['dish'] for dish in dishes]
    print(f'dish_names: {dish_names}')
    nutrition_info = await get_nutrition_info(dish_names)
    print(f'nutrition_info: {nutrition_info}')
    dishes = await get_final_output(json.dumps(gemini_output), json.dumps(nutrition_info), image_bytes)
    print(f'dishes: {dishes}')
    return dishes

