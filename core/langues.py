from core.parametres import LANGUE_ACTUELLE
from core.traductions import TRADUCTIONS

def traduire(clef, **kwargs):
    valeur = TRADUCTIONS.get(clef, {}).get(LANGUE_ACTUELLE, clef)
    if kwargs:
        try:
            return valeur.format(**kwargs)
        except Exception:
            return valeur
    return valeur
