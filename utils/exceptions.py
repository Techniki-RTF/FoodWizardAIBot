class ApiError(Exception):
    """Базовый класс для ошибок API"""
    def __init__(self, message="API error occurred"):
        self.message = message
        super().__init__(self.message)


class GeminiApiError(ApiError):
    """Ошибка при работе с Gemini API"""
    def __init__(self, message="Gemini API error occurred"):
        super().__init__(message)


class CalorieNinjasApiError(ApiError):
    """Ошибка при работе с CalorieNinjas API"""
    def __init__(self, message="CalorieNinjas API error occurred"):
        super().__init__(message)


class FoodNotRecognizedError(Exception):
    """Ошибка, когда еда не распознана"""
    def __init__(self, message="Food not recognized"):
        self.message = message
        super().__init__(self.message)


class EmptyResponseError(Exception):
    """Ошибка, когда API возвращает пустой ответ"""
    def __init__(self, message="Empty response received"):
        self.message = message
        super().__init__(self.message)


class NutritionDataNotFoundError(Exception):
    """Ошибка, когда данные о питательности не найдены"""
    def __init__(self, message="Nutrition data not found"):
        self.message = message
        super().__init__(self.message) 