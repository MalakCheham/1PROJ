from core.parametres import LANGUE_ACTUELLE
from core.traductions import TRADUCTIONS

def traduire(clef):
    return TRADUCTIONS.get(clef, {}).get(LANGUE_ACTUELLE, clef)
