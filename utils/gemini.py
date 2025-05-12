import json

from decouple import config
from google.genai.errors import APIError
from utils.gemini_constants import *
from google.genai.types import Tool, GoogleSearch

client = genai.Client(api_key=config("GEMINI_API_KEY"))
async def recognize_dish(image_bytes):
    contents = [types.Content(role="user", parts=[types.Part.from_text(text="Первый этап"), types.Part.from_bytes(data=image_bytes, mime_type="image/png")])]
    generate_content_config = types.GenerateContentConfig(response_mime_type="application/json", response_schema=RECOGNITION_RESPONSE_SCHEMA, system_instruction=RECOGNITION_SYSTEM_INSTRUCTION)
    try:
        response = json.loads(client.models.generate_content(
            model= "gemini-2.0-flash-lite",
            contents=contents,
            config=generate_content_config).text)
        if len(response['dishes']) == 0: return False
        return response
    except APIError as e:
        print(e)
        return 'api_error'

async def generate_nutrition_plan(daily_kcal, goal, preferences=None):
    prompt_text = f"Дневная норма калорий: {daily_kcal}, цель: {goal}"
    if preferences:
        prompt_text += f", предпочтения: {preferences}"
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)])]
    generate_content_config =  types.GenerateContentConfig(response_mime_type="application/json", response_schema=PLAN_RESPONSE_SCHEMA, system_instruction=PLAN_SYSTEM_INSTRUCTION)
    try:
        response = json.loads(client.models.generate_content(
            model= "gemini-2.5-flash-preview-04-17",
            contents=contents,
            config=generate_content_config).text)
        if len(response['days']) == 0: return 'api_error'
        print(response)
        return response
    except APIError as e:
        print(e)
        return 'api_error'

async def generate_recipe(dish, image_bytes):
    prompt_text = f"Блюдо: {dish}"
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)]), types.Part.from_bytes(data=image_bytes, mime_type="image/png")]
    generate_content_config =  types.GenerateContentConfig(response_mime_type="text/plain",
                                                           system_instruction=RECIPE_SYSTEM_INSTRUCTION,
                                                           tools=[genai.types.Tool(google_search=GoogleSearch())])
    try:
        response = client.models.generate_content(
            model= "gemini-2.5-flash-preview-04-17",
            contents=contents,
            config=generate_content_config)
        print(response)
        return await recipe_response_to_json(response)
    except APIError as e:
        print(e)
        return 'api_error'

async def recipe_response_to_json(response):
    prompt_text = f"Конвертируй свой предыдущий ответ в json: {response}"
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)])]
    generate_content_config = types.GenerateContentConfig(response_mime_type="application/json",
                                                          system_instruction=RECIPE_SYSTEM_INSTRUCTION,
                                                          response_schema=RECIPE_RESPONSE_SCHEMA)
    try:
        response = json.loads(client.models.generate_content(
            model= "gemini-2.5-flash-preview-04-17",
            contents=contents,
            config=generate_content_config).text)
        print(response)
        return response
    except APIError as e:
        print(e)
        return 'api_error'
