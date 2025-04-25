from decouple import config
from requests import get

api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
api_key = config("CALORIE_NINJAS_API_KEY")


async def get_nutrition_info(query):
    return get(api_url + ''.join(query), headers={'X-Api-Key': api_key}).json()