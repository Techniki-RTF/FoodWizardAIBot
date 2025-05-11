import json

from decouple import config
from google.genai.errors import APIError
from utils.gemini_constants import *

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

async def generate_nutrition_plan(daily_kcal, goal):
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=f"Дневная норма калорий: {daily_kcal}, цель: {goal}")])]
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