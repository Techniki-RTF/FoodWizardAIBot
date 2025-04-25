from google import genai
from google.genai import types

SYSTEM_INSTRUCTION = """
            Первый этап:
            Я буду отправлять фото еды, а ты должен распознать на фото еду и оценить примерный вес
            Если ты видишь, что несколько видов еды находятся в одной тарелке, то скорее всего это одно блюдо.
            Если блюд несколько, то перечисли все.
            Если блюдо не существует или тебе отправили не блюдо верни пустой Json.
            Названия блюд на английском языке и на русском языке.
            
            Второй этап:
            После я отправлю тебе то же самое изображение, твой прошлый ответ, ответ из Calorie Ninja API (запрос туда - твой прошлый ответ)
            Твоя задача сопоставить калории продуктов и другие их данные с блюдами, которые ты распознал.
            Названия блюд на СТРОГО русском языке (из dish_ru).
            Вернуть нужно соответсвующий JSON.
            """

RESPONSE_SCHEMA_FOR_RECOGNITION = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["dishes"],
    properties = {
        "dishes": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            description = "An array of dishes with their nutritional information.",
            items = genai.types.Schema(
                type = genai.types.Type.OBJECT,
                required = ["dish", "dish_ru", "weight"],
                properties = {
                    "dish": genai.types.Schema(
                        type = genai.types.Type.STRING,
                        description = "Name of the dish",
                    ),
                    "dish_ru": genai.types.Schema(
                        type=genai.types.Type.STRING,
                        description="Name of the dish in russian",
                    ),
                    "weight": genai.types.Schema(
                        type = genai.types.Type.INTEGER,
                        description = "Weight of the dish in grams",
                    ),
                },
            ),
        ),
    },
)

RESPONSE_SCHEMA_FOR_FINAL = genai.types.Schema(
        type=genai.types.Type.OBJECT,
        required=["dishes"],
        properties={
            "dishes": genai.types.Schema(
                type=genai.types.Type.ARRAY,
                description="An array of dishes with their nutritional information.",
                items=genai.types.Schema(
                    type=genai.types.Type.OBJECT,
                    required=["dish_ru", "weight", "calories_per_100g", "calories_per_total"],
                    properties={
                        "dish_ru": genai.types.Schema(
                            type=genai.types.Type.STRING,
                            description="Name of the dish in russian language (from previous dish_ru)",
                        ),
                        "weight": genai.types.Schema(
                            type=genai.types.Type.INTEGER,
                            description="Weight of the dish in grams (from your previous response)",
                        ),
                        "calories_per_100g": genai.types.Schema(
                            type=genai.types.Type.INTEGER,
                            description="Calories per 100 grams of the dish (from calories in API response)",
                        ),
                        "calories_per_total": genai.types.Schema(
                            type=genai.types.Type.INTEGER,
                            description="Total calories in the dish (multiply calories by weight)",
                        ),
                    },
                ),
            ),
        },
    )