import gettext

from db_handler.database import get_user_lang


def get_translator(lang):
    t = gettext.translation(
        domain='bot',
        localedir='locales',
        languages=[lang],
        fallback=True
    )
    return t.gettext

async def get_user_translator(user_id):
    lang = await get_user_lang(user_id)
    return get_translator(lang)