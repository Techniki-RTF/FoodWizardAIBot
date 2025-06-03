from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from typing import Union

from db_handler.database import get_profile, get_user_lang, create_user
from keyboards.inline_keyboard import main_menu_kb, profile_kb, goal_kb, lang_kb, back_home_kb, user_sex_kb, params_kb, daily_kcal_kb
from states import UserStates
from utils.converters import goal_converter, user_sex_converter, bmi_converter, activity_converter, bmi_to_goal_converter
from utils.delete_menu_message import delete_menu_message
from utils.locales import get_user_translator

async def show_main_menu(user_id: int, context: Union[Message, CallbackQuery], state: FSMContext, bot: Bot = None):
    _ = await get_user_translator(user_id)
    
    if isinstance(context, Message):
        await delete_menu_message(context, state, bot)
        await context.delete()
        answer = await context.answer(
            _("Hello, {name}!\nMenu:").format(name=context.from_user.full_name), 
            reply_markup=await main_menu_kb(user_id=user_id)
        )
    else:
        await delete_menu_message(context.message, state, bot)
        await context.answer()
        answer = await context.message.answer(
            _("Hello, {name}!\nMenu:").format(name=context.from_user.full_name), 
            reply_markup=await main_menu_kb(user_id=user_id)
        )
    
    await state.update_data(menu_message_id=answer.message_id)

async def show_main_menu_edit(user_id: int, callback: CallbackQuery, state: FSMContext):
    _ = await get_user_translator(user_id)
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await callback.message.edit_text(
        _("Hello, {name}!\nMenu:").format(name=callback.from_user.full_name), 
        reply_markup=await main_menu_kb(user_id=user_id)
    )

async def show_profile(user_id: int, context: Union[Message, CallbackQuery]):
    _ = await get_user_translator(user_id)
    c_profile = await get_profile(user_id)
    c_profile = {k: _("no data") if v in ('', None) else v for k, v in c_profile.items()}
    
    text = (
        _("Your goal: {goal}").format(goal=await goal_converter(c_profile['goal'], user_id)) + "\n" +
        _("Your sex: {sex}").format(sex=await user_sex_converter(c_profile['sex'], user_id)) + "\n" +
        _("Your current parameters: {height} cm / {weight} kg / {age} years").format(
            height=c_profile['height'], 
            weight=c_profile['weight'], 
            age=c_profile['age']
        ) + "\n" +
        _("Your Body Mass Index (BMI): {bmi}").format(
            bmi=await bmi_converter(c_profile['bmi'], user_id) if type(c_profile['bmi']) in {float, int} else _("no data")
        ) + "\n" +
        _("Your daily calorie allowance considering your activity level ({activity}): {daily_kcal}").format(
            activity=await activity_converter(c_profile['activity'], user_id),
            daily_kcal=c_profile['daily_kcal']
        )
    )
    
    if isinstance(context, Message):
        await context.answer(text, reply_markup=await profile_kb(user_id=user_id))
    else:
        await context.message.edit_text(text, reply_markup=await profile_kb(user_id=user_id))

async def show_goal_selection(user_id: int, context: Union[Message, CallbackQuery]):
    _ = await get_user_translator(user_id)
    c_profile = await get_profile(user_id)
    bmi = c_profile['bmi']
    text = _("Select your goal:") + (await bmi_to_goal_converter(bmi, user_id) if bmi else '')
    
    if isinstance(context, Message):
        await context.answer(text, reply_markup=await goal_kb(user_id=user_id, bmi=bmi))
    else:
        await context.message.edit_text(text, reply_markup=await goal_kb(user_id=user_id, bmi=bmi))

async def show_language_selection(context: Union[Message, CallbackQuery]):
    if isinstance(context, CallbackQuery):
        await context.message.edit_text('Выбери язык / Choose your language', reply_markup=await lang_kb())
    else:
        await context.answer('Выбери язык / Choose your language', reply_markup=await lang_kb())

async def show_about(user_id: int, context: Union[Message, CallbackQuery]):
    _ = await get_user_translator(user_id)
    text = _("Developer: t.me/renamq\nTeam: Techniki")
    
    if isinstance(context, Message):
        await context.answer(text, reply_markup=await back_home_kb(user_id=user_id))
    else:
        await context.message.edit_text(text, reply_markup=await back_home_kb(user_id=user_id))

async def show_send_image(user_id: int, context: Union[Message, CallbackQuery], state: FSMContext):
    _ = await get_user_translator(user_id)
    await state.set_state(UserStates.waiting_for_image)
    
    if isinstance(context, Message):
        answer = await context.answer(_("Send an image"), reply_markup=await back_home_kb(user_id=user_id))
        await state.update_data(original_message_id=answer.message_id)
    else:
        if hasattr(context, 'answer'):
            await context.answer()
        if context.message.photo:
            answer = await context.message.answer(text=_("Send an image"), reply_markup=await back_home_kb(user_id=user_id))
            await state.update_data(original_message_id=answer.message_id)
        else:
            await state.update_data(original_message_id=context.message.message_id)
            await context.message.edit_text(_("Send an image"), reply_markup=await back_home_kb(user_id=user_id))

async def show_user_sex_selection(user_id: int, context: Union[Message, CallbackQuery]):
    _ = await get_user_translator(user_id)
    text = _("Select your sex:")
    
    if isinstance(context, Message):
        await context.answer(text, reply_markup=await user_sex_kb(user_id=user_id))
    else:
        await context.message.edit_text(text, reply_markup=await user_sex_kb(user_id=user_id))

async def show_params_selection(user_id: int, context: Union[Message, CallbackQuery]):
    _ = await get_user_translator(user_id)
    text = _("Select a parameter to change its value")
    
    if isinstance(context, Message):
        await context.answer(text, reply_markup=await params_kb(user_id=user_id))
    else:
        await context.message.edit_text(text, reply_markup=await params_kb(user_id=user_id))

async def show_daily_kcal(user_id: int, context: Union[Message, CallbackQuery]):
    _ = await get_user_translator(user_id)
    c_profile = await get_profile(user_id)
    text = _("Select your activity level:")
    
    if isinstance(context, Message):
        await context.answer(text, reply_markup=await daily_kcal_kb(user_id=user_id, activity=c_profile['activity']))
    else:
        await context.message.edit_text(text, reply_markup=await daily_kcal_kb(user_id=user_id, activity=c_profile['activity']))

async def show_nutrition_plan(user_id: int, context: Union[Message, CallbackQuery], state: FSMContext):
    _ = await get_user_translator(user_id)
    c_profile = await get_profile(user_id)
    c_daily_kcal = c_profile['daily_kcal']
    
    if not c_daily_kcal:
        text = _("Please complete your profile and calculate your daily calorie allowance before using this feature.")
        if isinstance(context, Message):
            await context.answer(text, reply_markup=await back_home_kb(user_id=user_id))
        else:
            await context.message.edit_text(text, reply_markup=await back_home_kb(user_id=user_id))
        return
    
    text = _("Specify any dietary preferences, if you have them.\nExamples: desserts with meals, vegetarian diet, citrus intolerance.\nIf you have no special preferences, type \"None\".")
    await state.set_state(UserStates.waiting_for_diet_preferences)
    
    if isinstance(context, Message):
        answer = await context.answer(text, reply_markup=await back_home_kb(user_id=user_id))
        await state.update_data(original_message_id=answer.message_id)
    else:
        await state.update_data(original_message_id=context.message.message_id)
        await context.message.edit_text(text, reply_markup=await back_home_kb(user_id=user_id))

async def handle_start_command(user_id: int, context: Union[Message, CallbackQuery], state: FSMContext, bot: Bot = None):
    await create_user(user_id)
    if not await get_user_lang(user_id):
        await show_language_selection(context)
        return
    await show_main_menu(user_id, context, state, bot) 