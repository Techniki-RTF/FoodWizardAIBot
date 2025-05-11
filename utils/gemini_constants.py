from google import genai
from google.genai import types

SYSTEM_INSTRUCTION = """
            Я буду отправлять фото еды, а ты должен распознать на фото еду и оценить примерный вес
            Если ты видишь, что несколько видов еды находятся в одной тарелке, то скорее всего это одно блюдо.
            Если блюд несколько, то перечисли все.
            Если блюдо не существует или тебе отправили не блюдо верни пустой Json.
            Названия блюд на русском языке и перевод на английском для API Calorie Ninjas.
            """

RESPONSE_SCHEMA = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["dishes"],
    properties = {
        "dishes": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            description = "An array of dishes with their nutritional information.",
            items = genai.types.Schema(
                type = genai.types.Type.OBJECT,
                required = ["dish_ru", "dish_en", "weight"],
                properties = {
                    "dish_ru": genai.types.Schema(
                        type=genai.types.Type.STRING,
                        description="Name of the dish in russian",
                    ),
                    "dish_en": genai.types.Schema(
                        type=genai.types.Type.STRING,
                        description="Name of the dish in english (translate from russian, for CalorieNinjas API)",
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