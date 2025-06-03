import json
import asyncio

from decouple import config as env_config
from google.genai.errors import APIError
from utils.gemini_constants import *
from google.genai.types import Tool, GoogleSearch
from utils.exceptions import GeminiApiError, EmptyResponseError, FoodNotRecognizedError

client = genai.Client(api_key=env_config("GEMINI_API_KEY"))

async def make_gemini_api_request(model, contents, config, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config)
            return response
        except APIError as e:
            print(f"Attempt {attempt+1}/{max_attempts} caused exception: {e}")
            if attempt < max_attempts - 1:
                await asyncio.sleep(1)
            else:
                raise GeminiApiError(f"Gemini API failed after {max_attempts} attempts: {e}")
    return None

async def recognize_dish(image_bytes, user_lang):
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=f"ЯЗЫК ПОЛЬЗОВАТЕЛЯ: {user_lang}"), types.Part.from_text(text="Первый этап"), types.Part.from_bytes(data=image_bytes, mime_type="image/png")])]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json", 
        response_schema=RECOGNITION_RESPONSE_SCHEMA, 
        system_instruction=RECOGNITION_SYSTEM_INSTRUCTION
    )
    
    response = await make_gemini_api_request(
        model="gemini-2.5-flash-preview-05-20",
        contents=contents,
        config=generate_content_config
    )
    
    response = json.loads(response.text)
    if len(response['dishes']) == 0:
        raise FoodNotRecognizedError("No dishes recognized in the image")
    return response

async def generate_nutrition_plan(daily_kcal, goal, user_lang, preferences=None):
    prompt_text = f"Дневная норма калорий: {daily_kcal}, цель: {goal}"
    if preferences:
        prompt_text += f", предпочтения: {preferences}"
    
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=f"ЯЗЫК ПОЛЬЗОВАТЕЛЯ: {user_lang}"), types.Part.from_text(text=prompt_text)])]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json", 
        response_schema=PLAN_RESPONSE_SCHEMA, 
        system_instruction=PLAN_SYSTEM_INSTRUCTION
    )
    
    response = await make_gemini_api_request(
        model="gemini-2.5-flash-preview-05-20",
        contents=contents,
        config=generate_content_config
    )
    
    response = json.loads(response.text)
    if len(response['days']) == 0:
        raise EmptyResponseError("Generated plan contains no days")
    print(response)
    return response

async def generate_recipe(dish, image_bytes, user_lang):
    prompt_text = f"Блюдо: {dish}"
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=f"ЯЗЫК ПОЛЬЗОВАТЕЛЯ: {user_lang}"), types.Part.from_text(text=prompt_text)]), types.Part.from_bytes(data=image_bytes, mime_type="image/png")]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=RECIPE_SYSTEM_INSTRUCTION,
        tools=[genai.types.Tool(google_search=GoogleSearch())]
    )
    
    response = await make_gemini_api_request(
        model="gemini-2.5-flash-preview-05-20",
        contents=contents,
        config=generate_content_config
    )
    
    return await recipe_response_to_json(response)

async def recipe_response_to_json(response):
    prompt_text = f"Конвертируй свой предыдущий ответ в json: {response}"
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)])]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        system_instruction=RECIPE_SYSTEM_INSTRUCTION,
        response_schema=RECIPE_RESPONSE_SCHEMA
    )
    
    response = await make_gemini_api_request(
        model="gemini-2.5-flash-preview-05-20",
        contents=contents,
        config=generate_content_config
    )
    
    response = json.loads(response.text)
    print(response)
    return response

async def generate_food_swap(dishes, image_bytes, user_lang):
    prompt_text = f"Блюдо: {", ".join(dishes)}"
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=f"ЯЗЫК ПОЛЬЗОВАТЕЛЯ: {user_lang}"), types.Part.from_text(text=prompt_text)]), types.Part.from_bytes(data=image_bytes, mime_type="image/png")]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        system_instruction=FOOD_SWAP_SYSTEM_INSTRUCTION,
        response_schema=FOOD_SWAP_RESPONSE_SCHEMA
    )
    
    response = await make_gemini_api_request(
        model="gemini-2.5-flash-preview-05-20",
        contents=contents,
        config=generate_content_config
    )
    
    response = json.loads(response.text)
    print(response)
    return response
