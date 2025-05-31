from utils.gemini import recognize_dish
from utils.calorie_ninjas import get_nutrition_info

async def get_output(image_bytes, user_lang):
    gemini_output = await recognize_dish(image_bytes, user_lang=user_lang)
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
            protein_per_100g = nutrition_info['items'][0]['protein_g']
            fat_per_100g = nutrition_info['items'][0]['fat_total_g']
            carbs_per_100g = nutrition_info['items'][0]['carbohydrates_total_g']
            dishes_list[i]['calories_per_100g'] = int(calories_per_100g)
            dishes_list[i]['calories_per_total'] = int(dishes_list[i]['weight'] * calories_per_100g / 100)
            dishes_list[i]['pfc_per_100g'] = {
                'protein': round(protein_per_100g, 1),
                'fats': round(fat_per_100g, 1),
                'carbs': round(carbs_per_100g, 1)
            }
            dishes_list[i]['pfc_per_total'] = {
                'protein': round(dishes_list[i]['weight'] * protein_per_100g / 100, 1),
                'fats': round(dishes_list[i]['weight'] * fat_per_100g / 100, 1),
                'carbs': round(dishes_list[i]['weight'] * carbs_per_100g / 100, 1)
            }
        else:
            return False

    print(dishes_list)
    return {'dishes': dishes_list}

