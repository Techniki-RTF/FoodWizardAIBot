from decouple import config
from google import genai
from google.genai import types


def generate_nutrition(image_bytes):
    client = genai.Client(
        api_key=config("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash-lite"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["dishes"],
            properties = {
                "dishes": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    description = "An array of dishes with their nutritional information.",
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["dish", "weight", "calories_per_100g", "calories_per_total"],
                        properties = {
                            "dish": genai.types.Schema(
                                type = genai.types.Type.STRING,
                                description = "Name of the dish",
                            ),
                            "weight": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                                description = "Weight of the dish in grams",
                            ),
                            "calories_per_100g": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                                description = "Calories per 100 grams of the dish",
                            ),
                            "calories_per_total": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                                description = "Total calories in the dish",
                            ),
                        },
                    ),
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(text=
            """
            Я буду отправлять фото еды, а ты должен распознать на фото еду (1), оценить примерный вес (2), оценить калорийность на примерный вес (3), оценить калорийность на 100 грамм (4) и ответить в таком формате:
            \"Еда (1)  / калории (3) (примерный вес (2)) / калории (4) (100 грамм)\"
            ПРИМЕР: \"Красный перец / 9-12 ккал (30-40 грамм) / 31 ккал (100 грамм)\"
            Если ты видишь, что несколько видов еды находятся в одной тарелке, то скорее всего это одно блюдо.
            Если блюд несколько, то перечисли все. Каждое новое блюдо с новой строки, без нумерации строк.
            Если блюдо не существует или тебе отправили не блюдо верни пустой Json.
            """),
        ],
    )

    response =  client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    print(response.text)
    return response.text