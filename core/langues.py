from core.parametres import CURRENT_LANGUAGE
from core.traductions import TRANSLATIONS

""""Translate text"""

def translate(key, **kwargs):
    value = TRANSLATIONS.get(key, {}).get(CURRENT_LANGUAGE, key)
    if kwargs:
        try:
            return value.format(**kwargs)
        except Exception:
            return value
    return value
