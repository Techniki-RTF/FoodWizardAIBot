# Food Wizard AI Bot
### Telegram-бот для распознования блюд по фото и предоставлении информации о КБЖУ с дополнительными функциями для здорового питания.
Написан **Aiogram 3**, используется API **Gemini** и **Calorie Ninjas**. База данных - **SQLite**.

## Инструкция

### .env файл должен содержать следующие переменные:<br>
```TOKEN``` - Токен Telegram-бота из [BotFather](t.me/BotFather)<br>
```GEMINI_API_KEY``` - Ключ API Google Gemini из [Google AI Studio](https://aistudio.google.com/apikey)<br>
```CALORIE_NINJAS_API_KEY``` - Ключ API [Calorie Ninjas](https://calorieninjas.com/api)<br>
```ADMINS``` - Telegram ID администратора бота<br>

### Запуск бота:
```
pip install -r requirements.txt
python aiogram_run.py
```
[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/ZfDJXS?referralCode=AMG_G2)
