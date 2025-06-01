from core.traductions import TRANSLATIONS

""""Translate text"""

def translate(key, **kwargs):
    from core.parametres import CURRENT_LANGUAGE
    value = TRANSLATIONS.get(key, {}).get(CURRENT_LANGUAGE, key)
    if kwargs:
        try:
            return value.format(**kwargs)
        except Exception:
            return value
    return value
