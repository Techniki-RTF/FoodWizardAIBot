import json

from decouple import config
from google.genai.errors import APIError
from utils.gemini_constants import *

client = genai.Client(api_key=config("GEMINI_API_KEY"))
model = "gemini-2.0-flash-lite"

# async def create_cache(response, image_bytes):
#     try:
#         return client.caches.create(model=model, config=types.CreateCachedContentConfig(system_instruction=SYSTEM_INSTRUCTION, contents=[types.Part.from_text(text=SYSTEM_INSTRUCTION), types.Part.from_bytes(data=image_bytes, mime_type="image/png"), types.Part.from_text(text=response)], ttl="300s"))
#     except APIError as e:
#         print(e)
#         return 'api_error'

async def recognize_dish(image_bytes):
    contents = [types.Content(role="user", parts=[types.Part.from_text(text="Первый этап"), types.Part.from_bytes(data=image_bytes, mime_type="image/png")])]
    generate_content_config = types.GenerateContentConfig(response_mime_type="application/json", response_schema=RESPONSE_SCHEMA_FOR_RECOGNITION)
    try:
        response = json.loads(client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config).text)
        if len(response['dishes']) == 0: return False
        return response
    except APIError as e:
        print(e)
        return 'api_error'

async def get_final_output(gemini_output, nutrition_info, image_bytes):
    contents = [types.Content(role="user", parts=[types.Part.from_text(text="Второй этап"), types.Part.from_text(text=gemini_output), types.Part.from_bytes(data=image_bytes, mime_type="image/png"), types.Part.from_text(text=nutrition_info)])]
    generate_content_config = types.GenerateContentConfig(response_mime_type="application/json", response_schema=RESPONSE_SCHEMA_FOR_FINAL)
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config).text
        print(response)
        try:
            response = json.loads(response)
        except json.JSONDecodeError as e:
            print(e)
            return 'api_error'
        if len(response['dishes']) == 0: return False
        return response
    except APIError as e:
        print(e)
        return 'api_error'