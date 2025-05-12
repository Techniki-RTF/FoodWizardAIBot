from google import genai
from google.genai import types

RECOGNITION_SYSTEM_INSTRUCTION = """
            Я буду отправлять фото еды, а ты должен распознать на фото еду и оценить примерный вес
            Если ты видишь, что несколько видов еды находятся в одной тарелке, то скорее всего это одно блюдо.
            Если блюд несколько, то перечисли все.
            Если блюдо не существует или тебе отправили не блюдо верни пустой Json.
            Названия блюд на русском языке и перевод на английском для API Calorie Ninjas.
            """

RECOGNITION_RESPONSE_SCHEMA = genai.types.Schema(
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

PLAN_SYSTEM_INSTRUCTION = """
        Ты - ассистент в похудении/поддержании веса/наборе массы.
        Пользователь указывает свою цель и дневную норму калорий с учётом цели.
        Твоя задача - составить план питания на неделю.
        Нужно указать КБЖУ каждого дня, учесть дневную норму калорий, цель, индивидуальные предпочтения и диету, если они указаны.
        Ответ должен быть на русском языке.
        КРИТИЧНО ВАЖНО:
        Учти, что весь текст должен уложиться в 4096 символов (ограничение Telegram).
        """

meals_items = genai.types.Schema(
                            type=genai.types.Type.OBJECT,
                            required = ["dish_name", "description", "calories", "proteins", "fats", "carbs"],
                            properties = {
                                "dish_name": genai.types.Schema(
                                    type=genai.types.Type.STRING,
                                    description="Name of the dish."
                                ),
                                "description": genai.types.Schema(
                                    type=genai.types.Type.STRING,
                                    description="Brief description or ingredients of the dish."
                                ),
                                "calories": genai.types.Schema(
                                    type=genai.types.Type.INTEGER,
                                    description="Number of calories in this dish."
                                ),
                                "proteins": genai.types.Schema(
                                    type=genai.types.Type.INTEGER,
                                    description="Number of proteins in this dish."
                                ),
                                "fats": genai.types.Schema(
                                    type=genai.types.Type.INTEGER,
                                    description="Number of fats in this dish."
                                ),
                                "carbs": genai.types.Schema(
                                    type=genai.types.Type.INTEGER,
                                    description="Number of carbs in this dish."
                                ),
                            }
                        )


PLAN_RESPONSE_SCHEMA = genai.types.Schema(
    type=genai.types.Type.OBJECT,
    required = ["days"],
    properties = {
        "days": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            description = "Seven days of week.",
            min_items=7,
            max_items=7,
            items = genai.types.Schema(
                type = genai.types.Type.OBJECT,
                required = ["day_name", "breakfast", "lunch", "dinner", "calories", "proteins", "fats", "carbs"],
                properties = {
                    "day_name": genai.types.Schema(
                        type=genai.types.Type.STRING,
                        description = "Name of the day of the week in Russian, e.g., 'Понедельник', 'Вторник', etc.",
                    ),
                    "breakfast": genai.types.Schema(
                        type = genai.types.Type.ARRAY,
                        description = "List of dishes for breakfast.",
                        items = meals_items
                    ),
                    "lunch": genai.types.Schema(
                        type = genai.types.Type.ARRAY,
                        description = "List of dishes for lunch.",
                        items=meals_items
                    ),
                    "dinner": genai.types.Schema(
                        type = genai.types.Type.ARRAY,
                        description = "List of dishes for dinner.",
                        items = meals_items
                    ),
                    "calories": genai.types.Schema(
                        type = genai.types.Type.INTEGER,
                        description = "Total number of calories for this day.",
                    ),
                    "proteins": genai.types.Schema(
                        type=genai.types.Type.INTEGER,
                        description="Total number of proteins for this day.",
                    ),
                    "fats": genai.types.Schema(
                        type=genai.types.Type.INTEGER,
                        description="Total number of fats for this day.",
                    ),
                    "carbs": genai.types.Schema(
                        type=genai.types.Type.INTEGER,
                        description="Total number of carbs for this day.",
                    ),
                }
            )
        ),
        "commentary": genai.types.Schema(
            type=genai.types.Type.STRING,
            description = "Short commentary text for user about this nutrition plan",
        )
    }
)

RECIPE_SYSTEM_INSTRUCTION = """
            Ты - ассистент в подборе питания.
            Тебе передано название блюда (или блюд) и его (их) фото.
            Твоя задача - найти низкокалорийный рецепт.
            В твоём ответе обязательно должны быть: Название блюда, список ингредиентов, пошаговый рецепт, КБЖУ на 100г готового блюда.
            КРИТИЧНО ВАЖНО:
            Учти, что весь текст должен уложиться в менее 4096 символов (ограничение Telegram, MEDIA_CAPTION_TOO_LONG).
            """

RECIPE_RESPONSE_SCHEMA = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["recipes"],
    properties = {
        "recipes": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            description = "An array of dishes with their low-calorie recipes and nutritional information.",
            items = genai.types.Schema(
                type = genai.types.Type.OBJECT,
                required = ["dish_name", "ingredients", "recipe", "nutritional_info"],
                properties = {
                    "dish_name": genai.types.Schema(
                        type=genai.types.Type.STRING,
                        description="Name of the low-calorie dish in Russian.",
                    ),
                    "ingredients": genai.types.Schema(
                        type=genai.types.Type.ARRAY,
                        description="List of ingredients for this low-calorie dish.",
                        items=genai.types.Schema(
                            type=genai.types.Type.STRING,
                            description="An ingredient, e.g., '200г куриной грудки'",
                        ),
                    ),
                    "recipe": genai.types.Schema(
                        type = genai.types.Type.ARRAY,
                        description = "Step-by-step instructions for preparing the low-calorie dish.",
                         items=genai.types.Schema(
                            type=genai.types.Type.STRING,
                            description="One step of the recipe, e.g., 'Нарежьте куриную грудку кубиками.'",
                        ),
                    ),
                    "nutritional_info": genai.types.Schema(
                        type=genai.types.Type.OBJECT,
                        description="Nutritional information for 100g of the finished low-calorie dish.",
                        required=["calories", "protein", "fats", "carbs"],
                        properties={
                            "calories": genai.types.Schema(
                                type=genai.types.Type.NUMBER,
                                description="Calories per 100g in kcal."
                            ),
                            "protein": genai.types.Schema(
                                type=genai.types.Type.NUMBER,
                                description="Protein per 100g in grams."
                            ),
                            "fats": genai.types.Schema(
                                type=genai.types.Type.NUMBER,
                                description="Fats per 100g in grams."
                            ),
                            "carbs": genai.types.Schema(
                                type=genai.types.Type.NUMBER,
                                description="Carbohydrates per 100g in grams."
                            ),
                        }
                    )
                },
            ),
        ),
    },
)