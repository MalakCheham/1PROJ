from core.parametres import get_language
from core.traductions import TRADUCTIONS


def translate(key):
    current_lang = get_language()
    return TRADUCTIONS.get(key, {}).get(current_lang, key)
