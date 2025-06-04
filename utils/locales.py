import gettext
from typing import Union, Callable, Optional

from aiogram.types import Message, CallbackQuery
from db_handler.database import get_user_lang


def get_translator(lang):
    if lang is None:
        lang = 'ru'
        
    t = gettext.translation(
        domain='bot',
        localedir='locales',
        languages=[lang],
        fallback=True
    )
    return t.gettext

_redirect_in_progress = False

async def get_user_translator(user_id, context: Optional[Union[Message, CallbackQuery]] = None) -> Callable:
    global _redirect_in_progress
    
    lang = await get_user_lang(user_id)
    
    if lang is None and context is not None and not _redirect_in_progress:
        _redirect_in_progress = True
        
        from keyboards.inline_keyboard import lang_kb
        
        if isinstance(context, CallbackQuery):
            await context.message.edit_text('Выбери язык / Choose your language', reply_markup=await lang_kb())
        else:
            await context.answer('Выбери язык / Choose your language', reply_markup=await lang_kb())
        
        _redirect_in_progress = False
    
    return get_translator(lang)