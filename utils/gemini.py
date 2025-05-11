import json

from decouple import config
from google.genai.errors import APIError
from utils.gemini_constants import *

client = genai.Client(api_key=config("GEMINI_API_KEY"))
model = "gemini-2.0-flash-lite"

async def recognize_dish(image_bytes):
    contents = [types.Content(role="user", parts=[types.Part.from_text(text="Первый этап"), types.Part.from_bytes(data=image_bytes, mime_type="image/png")])]
    generate_content_config = types.GenerateContentConfig(response_mime_type="application/json", response_schema=RESPONSE_SCHEMA)
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