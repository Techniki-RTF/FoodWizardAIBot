from utils.gemini import recognize_dish
from utils.calorie_ninjas import get_nutrition_info

async def get_output(image_bytes):
    gemini_output = await recognize_dish(image_bytes)
    print(f'gemini_output: {gemini_output}')
    
    if gemini_output == 'api_error' or gemini_output is False:
        return gemini_output
        
    dishes_list = gemini_output['dishes']
    dish_names = [dish['dish_en'] for dish in dishes_list]
    print(f'dish_names: {dish_names}')
    
    for i, dish in enumerate(dishes_list):
        dish_name = dish['dish_en']
        nutrition_info = await get_nutrition_info(dish_name)
        print(f'nutrition_info: {nutrition_info}')

        if 'items' in nutrition_info and len(nutrition_info['items']) > 0:
            calories_per_100g = nutrition_info['items'][0]['calories']
            dishes_list[i]['calories_per_100g'] = int(calories_per_100g)
            dishes_list[i]['calories_per_total'] = int(dishes_list[i]['weight'] * calories_per_100g / 100)
        else:
            return False

    print(dishes_list)
    return {'dishes': dishes_list}

